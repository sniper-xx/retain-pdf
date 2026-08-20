from __future__ import annotations

import json
import os
import re
import socket
import threading
import time
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from foundation.shared.local_env import get_secret
from services.translation.diagnostics import get_active_translation_run_diagnostics
from services.translation.diagnostics import infer_stage_from_request_label
from services.translation.llm.shared.prompt_building import build_messages
from services.translation.llm.shared.prompt_building import build_single_item_fallback_messages
from services.translation.llm.shared.response_parsing import extract_json_text
from services.translation.llm.shared.response_parsing import extract_single_item_translation_text
from services.translation.llm.shared.response_parsing import unwrap_translation_shell


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_API_KEY_FILE = "openai.env"
TRUST_ENV_PROXY_ENV = "PDF_TRANSLATOR_TRUST_ENV_PROXY"
STREAM_RESPONSES_ENV = "PDF_TRANSLATOR_OPENAI_STREAM"
_THREAD_LOCAL = threading.local()
HTTP_RETRY_ATTEMPTS = 2
DNS_RETRY_MIN_ATTEMPTS = 3
HTTP_RETRY_BACKOFF_MAX_SECS = 20
HTTP_RATE_LIMIT_WAIT_MAX_SECS = 300
_TRANSPORT_RETRY_MARKERS = (
    "temporary failure in name resolution",
    "name resolution",
    "failed to resolve",
    "max retries exceeded",
    "connection aborted",
    "connection reset",
    "connection refused",
    "connect timeout",
    "read timeout",
    "timed out",
    "server disconnected",
    "remote end closed connection",
    "service unavailable",
    "bad gateway",
    "gateway timeout",
    "too many requests",
)
_TRANSPORT_STATUS_CODES = {408, 429, 500, 502, 503, 504}
_DNS_RETRY_MARKERS = (
    "temporary failure in name resolution",
    "name resolution",
    "failed to resolve",
    "nodename nor servname provided",
    "no address associated with hostname",
    "getaddrinfo failed",
)
_DNS_CACHE_TTL_SECS = 60
_DNS_CACHE_LOCK = threading.Lock()
_DNS_CACHE: dict[str, float] = {}


def normalize_base_url(base_url: str) -> str:
    normalized = (base_url or DEFAULT_BASE_URL).strip().rstrip("/")
    if normalized.endswith("/chat/completions"):
        normalized = normalized[: -len("/chat/completions")]
    return normalized


def _hostname_from_base_url(base_url: str) -> str:
    parsed = urlparse(normalize_base_url(base_url))
    return str(parsed.hostname or "").strip().lower()


def is_dns_resolution_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in _DNS_RETRY_MARKERS)


def _prewarm_dns(base_url: str, *, request_label: str = "") -> None:
    hostname = _hostname_from_base_url(base_url)
    if not hostname:
        return
    now = time.time()
    with _DNS_CACHE_LOCK:
        cached_until = _DNS_CACHE.get(hostname, 0.0)
        if cached_until > now:
            return
    try:
        socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
    except OSError as exc:
        if request_label:
            print(f"{request_label}: dns prewarm skipped host={hostname}: {type(exc).__name__}: {exc}", flush=True)
        return
    with _DNS_CACHE_LOCK:
        _DNS_CACHE[hostname] = now + _DNS_CACHE_TTL_SECS
    if request_label:
        print(f"{request_label}: dns prewarm ok host={hostname}", flush=True)


def chat_completions_url(base_url: str) -> str:
    return f"{normalize_base_url(base_url)}/chat/completions"


def build_headers(api_key: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    org = os.environ.get("OPENAI_ORG_ID", "").strip()
    if org:
        headers["OpenAI-Organization"] = org
    project = os.environ.get("OPENAI_PROJECT_ID", "").strip()
    if project:
        headers["OpenAI-Project"] = project
    return headers


def _message_chars(messages: list[dict[str, str]]) -> int:
    total = 0
    for message in messages:
        if not isinstance(message, dict):
            continue
        total += len(str(message.get("content", "") or ""))
    return total


def _body_bytes(body: dict[str, Any]) -> int:
    return len(json.dumps(body, ensure_ascii=False).encode("utf-8"))


def _response_text_excerpt(response: requests.Response, *, max_chars: int = 800) -> str:
    try:
        text = response.text or ""
    except Exception as exc:  # noqa: BLE001
        return f"<failed to read response body: {type(exc).__name__}: {exc}>"
    compact = " ".join(text.strip().split())
    if len(compact) > max_chars:
        return f"{compact[:max_chars]}...<truncated>"
    return compact


def _request_meta_summary(
    *,
    model: str,
    messages: list[dict[str, str]],
    body: dict[str, Any],
    use_stream: bool,
) -> str:
    response_format = body.get("response_format")
    response_format_type = (
        str(response_format.get("type", "") or "")
        if isinstance(response_format, dict)
        else ("present" if response_format is not None else "none")
    )
    return (
        f"model={model} messages={len(messages)} message_chars={_message_chars(messages)} "
        f"body_bytes={_body_bytes(body)} stream={use_stream} response_format={response_format_type or 'none'}"
    )


def _raise_for_status_with_context(
    response: requests.Response,
    *,
    model: str,
    messages: list[dict[str, str]],
    body: dict[str, Any],
    use_stream: bool,
) -> None:
    status_code = int(getattr(response, "status_code", 200) or 200)
    if status_code < 400:
        return
    response_body = _response_text_excerpt(response) or "<empty>"
    reason = getattr(response, "reason", "") or "Error"
    url = getattr(response, "url", "") or "<unknown-url>"
    raise requests.HTTPError(
        f"{status_code} Client Error: {reason} for url: {url} | "
        f"response_body={response_body} | "
        f"request_meta={_request_meta_summary(model=model, messages=messages, body=body, use_stream=use_stream)}",
        response=response,
    )


def should_use_stream_responses() -> bool:
    value = os.environ.get(STREAM_RESPONSES_ENV, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def should_trust_env_proxy() -> bool:
    value = os.environ.get(TRUST_ENV_PROXY_ENV, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = should_trust_env_proxy()
    if not session.trust_env:
        session.proxies.clear()
    diagnostics = get_active_translation_run_diagnostics()
    pool_size = 10
    if diagnostics is not None and diagnostics.provider_family.startswith("openai"):
        pool_size = min(256, max(32, int(diagnostics.configured_workers)))
    adapter = HTTPAdapter(
        pool_connections=pool_size,
        pool_maxsize=pool_size,
        max_retries=Retry(
            total=0,
            connect=0,
            read=0,
            redirect=0,
            status=0,
            backoff_factor=0,
        ),
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _drop_session(session_key: str) -> None:
    session = getattr(_THREAD_LOCAL, session_key, None)
    if session is not None:
        try:
            session.close()
        except Exception:
            pass
        setattr(_THREAD_LOCAL, session_key, None)


def get_session() -> requests.Session:
    session_key = "session_trust_env" if should_trust_env_proxy() else "session_direct"
    session = getattr(_THREAD_LOCAL, session_key, None)
    if session is None:
        session = _build_session()
        setattr(_THREAD_LOCAL, session_key, session)
    return session


def _request_session_key() -> str:
    return "session_trust_env" if should_trust_env_proxy() else "session_direct"


def is_transport_error(exc: Exception) -> bool:
    if isinstance(exc, (ValueError, KeyError, json.JSONDecodeError)):
        return False
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True
    text = str(exc).lower()
    if any(marker in text for marker in _TRANSPORT_RETRY_MARKERS):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return exc.response.status_code in _TRANSPORT_STATUS_CODES
    return isinstance(exc, requests.RequestException)


def _retry_delay(attempt: int) -> int:
    return min(HTTP_RETRY_BACKOFF_MAX_SECS, 2 * attempt)


def _retry_after_delay(exc: Exception, attempt: int) -> tuple[int, str]:
    if isinstance(exc, requests.HTTPError) and exc.response is not None and exc.response.status_code == 429:
        header = str(exc.response.headers.get("Retry-After", "") or "").strip()
        if header.isdigit():
            return max(1, int(header)), "retry_after"
    return _retry_delay(attempt), "backoff"


def _extract_stream_delta_text(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list):
        return ""
    chunks: list[str] = []
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        delta = choice.get("delta")
        if isinstance(delta, dict):
            content = delta.get("content")
            if isinstance(content, str):
                chunks.append(content)
    return "".join(chunks)


def _consume_streaming_response(response: requests.Response) -> str:
    chunks: list[str] = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        line_str = line.strip()
        if not line_str.startswith("data:"):
            continue
        payload_str = line_str[len("data:") :].strip()
        if payload_str == "[DONE]":
            break
        try:
            data = json.loads(payload_str)
        except Exception:
            continue
        delta = _extract_stream_delta_text(data)
        if delta:
            chunks.append(delta)
    return "".join(chunks)


def get_api_key(api_key: str = "", default_env: str = DEFAULT_API_KEY_ENV) -> str:
    key = (api_key or os.environ.get(default_env, "")).strip()
    if not key:
        key = get_secret(default_env, DEFAULT_API_KEY_FILE).strip()
    return key


def request_chat_content(
    messages: list[dict[str, str]],
    *,
    api_key: str = "",
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    temperature: float = 0.0,
    response_format: dict[str, Any] | None = None,
    timeout: int = 120,
    request_label: str = "",
    max_attempts: int | None = None,
) -> str:
    effective_api_key = get_api_key(api_key)
    headers = build_headers(effective_api_key)
    target_url = chat_completions_url(base_url)
    use_stream = should_use_stream_responses()

    is_reasoning_model = any(model.lower().startswith(p) for p in ("o1", "o3", "gpt-5-reasoning"))

    body: dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "stream": use_stream,
    }
    if not is_reasoning_model:
        body["temperature"] = temperature

    if response_format is not None:
        body["response_format"] = response_format

    total_attempts = max_attempts if max_attempts is not None else HTTP_RETRY_ATTEMPTS
    attempts = max(1, total_attempts)

    _prewarm_dns(base_url, request_label=request_label)

    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        session = get_session()
        try:
            response = session.post(target_url, headers=headers, json=body, timeout=timeout)
            _raise_for_status_with_context(
                response,
                model=model,
                messages=messages,
                body=body,
                use_stream=use_stream,
            )
            if use_stream:
                content = _consume_streaming_response(response)
            else:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
            return content or ""
        except Exception as exc:
            last_exc = exc
            is_transport = is_transport_error(exc)
            if not is_transport or attempt >= attempts:
                raise
            delay, _ = _retry_after_delay(exc, attempt)
            time.sleep(delay)

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Request failed without an exception")
