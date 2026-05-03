# Redis Unavailable Runbook

1. Check `/ready` and confirm `redis: unavailable`.
2. Check `docker compose ps redis`.
3. Inspect logs with `docker compose logs redis`.
4. Restart locally with `docker compose restart redis`.
5. Expect cache bypass and rate-limit fail-closed behavior while Redis is unavailable.
