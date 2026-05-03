#!/usr/bin/env bash
set -euo pipefail

docker compose stop redis
curl -sS http://localhost:8000/ready
docker compose start redis
