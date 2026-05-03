#!/usr/bin/env bash
set -euo pipefail

docker compose stop model-server
curl -sS -o /tmp/ai-docops-model-down.json -w "%{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ak_dev_tenant_a_123456" \
  -d '{"text":"The model server is down. The API should return 503.","max_sentences":1,"language":"en"}' \
  http://localhost:8000/v1/summaries
cat /tmp/ai-docops-model-down.json
docker compose start model-server
