import unittest
from pathlib import Path
from unittest import mock

REPO_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0, str(REPO_SCRIPTS_ROOT))

from services.translation.llm.shared.provider_registry import (
    DEEPSEEK_RUNTIME,
    OPENAI_RUNTIME,
    PROVIDER_REGISTRY,
    resolve_active_provider_runtime,
)
from services.translation.llm.providers.openai.client import (
    DEFAULT_BASE_URL as OPENAI_DEFAULT_BASE_URL,
    DEFAULT_MODEL as OPENAI_DEFAULT_MODEL,
    build_headers as openai_build_headers,
    chat_completions_url as openai_chat_completions_url,
    normalize_base_url as openai_normalize_base_url,
    request_chat_content as openai_request_chat_content,
)
from services.translation.llm.providers.openai.translation_client import (
    parse_translation_payload as openai_parse_translation_payload,
)


class OpenAIProviderTests(unittest.TestCase):
    def test_provider_registry_contains_openai_and_deepseek(self):
        self.assertIn("openai", PROVIDER_REGISTRY)
        self.assertIn("deepseek", PROVIDER_REGISTRY)
        self.assertEqual(OPENAI_RUNTIME.provider_id, "openai")
        self.assertEqual(OPENAI_RUNTIME.default_model, "gpt-4o")
        self.assertEqual(OPENAI_RUNTIME.default_base_url, "https://api.openai.com/v1")

    def test_resolve_active_provider_runtime_by_id(self):
        runtime = resolve_active_provider_runtime("openai")
        self.assertEqual(runtime.provider_id, "openai")
        self.assertEqual(runtime.provider_family, "openai_official")

        runtime_ds = resolve_active_provider_runtime("deepseek")
        self.assertEqual(runtime_ds.provider_id, "deepseek")

    def test_resolve_active_provider_runtime_by_model_and_url(self):
        runtime_gpt = resolve_active_provider_runtime(model="gpt-4o-mini")
        self.assertEqual(runtime_gpt.provider_id, "openai")

        runtime_o3 = resolve_active_provider_runtime(model="o3-mini")
        self.assertEqual(runtime_o3.provider_id, "openai")

        runtime_openai_url = resolve_active_provider_runtime(base_url="https://api.openai.com/v1")
        self.assertEqual(runtime_openai_url.provider_id, "openai")

        runtime_ds_url = resolve_active_provider_runtime(base_url="https://api.deepseek.com/v1")
        self.assertEqual(runtime_ds_url.provider_id, "deepseek")

    def test_openai_url_and_headers(self):
        self.assertEqual(
            openai_chat_completions_url("https://api.openai.com/v1"),
            "https://api.openai.com/v1/chat/completions",
        )
        self.assertEqual(
            openai_chat_completions_url("https://api.openai.com/v1/chat/completions"),
            "https://api.openai.com/v1/chat/completions",
        )
        headers = openai_build_headers("sk-test123456")
        self.assertEqual(headers["Authorization"], "Bearer sk-test123456")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_openai_parse_tagged_payload(self):
        tagged_text = "<<<ITEM item_id=p001-b001 decision=translate>>>这是译文内容<<<END>>>"
        parsed = openai_parse_translation_payload(tagged_text)
        self.assertIn("p001-b001", parsed)
        self.assertEqual(parsed["p001-b001"]["decision"], "translate")
        self.assertEqual(parsed["p001-b001"]["translated_text"], "这是译文内容")

    def test_openai_parse_json_payload(self):
        json_text = '{"translations": [{"item_id": "p002-b003", "translated_text": "深度学习翻译", "decision": "translate"}]}'
        parsed = openai_parse_translation_payload(json_text)
        self.assertIn("p002-b003", parsed)
        self.assertEqual(parsed["p002-b003"]["decision"], "translate")
        self.assertEqual(parsed["p002-b003"]["translated_text"], "深度学习翻译")

    @mock.patch("services.translation.llm.providers.openai.client.get_session")
    def test_openai_request_chat_content(self, mock_get_session):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "<<<ITEM item_id=item-1>>>Translated Text<<<END>>>"
                    }
                }
            ]
        }
        mock_session = mock.Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        content = openai_request_chat_content(
            [{"role": "user", "content": "Translate"}],
            api_key="sk-test",
            model="gpt-4o",
        )
        self.assertIn("Translated Text", content)


if __name__ == "__main__":
    unittest.main()
