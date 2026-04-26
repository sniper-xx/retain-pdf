#!/usr/bin/env sh
set -eu

: "${FRONT_API_BASE:=}"
: "${FRONT_X_API_KEY:=}"
: "${FRONT_OCR_PROVIDER:=paddle}"
: "${FRONT_MINERU_TOKEN:=}"
: "${FRONT_PADDLE_TOKEN:=}"
: "${FRONT_PADDLE_API_URL:=}"
: "${FRONT_MODEL_API_KEY:=}"
: "${FRONT_MODEL:=deepseek-v4-flash}"
: "${FRONT_BASE_URL:=https://api.deepseek.com/v1}"

if [ -n "$FRONT_API_BASE" ]; then
  API_BASE_VALUE="\"$FRONT_API_BASE\""
else
  API_BASE_VALUE="window.location.origin"
fi

cat > /usr/share/nginx/html/runtime-config.js <<EOF
window.__FRONT_RUNTIME_CONFIG__ = {
  apiBase: ${API_BASE_VALUE},
  xApiKey: "${FRONT_X_API_KEY}",
  ocrProvider: "${FRONT_OCR_PROVIDER}",
  mineruToken: "${FRONT_MINERU_TOKEN}",
  paddleToken: "${FRONT_PADDLE_TOKEN}",
  paddleApiUrl: "${FRONT_PADDLE_API_URL}",
  modelApiKey: "${FRONT_MODEL_API_KEY}",
  model: "${FRONT_MODEL}",
  baseUrl: "${FRONT_BASE_URL}",
};
EOF

if [ ! -f /usr/share/nginx/html/runtime-config.local.js ]; then
  printf '%s\n' '// Optional local runtime overrides are intentionally empty in Docker.' \
    > /usr/share/nginx/html/runtime-config.local.js
fi
