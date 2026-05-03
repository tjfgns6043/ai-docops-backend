#!/usr/bin/env bash
set -euo pipefail

docker compose stop postgres
curl -sS http://localhost:8000/ready
docker compose start postgres
