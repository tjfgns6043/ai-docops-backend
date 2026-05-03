# Failure Scenarios

## Model Server Down

Run:

```bash
scripts/failure_model_down.sh
```

Expected result:

- `/v1/summaries` returns `503`.
- Error code is `MODEL_UNAVAILABLE` or `MODEL_TIMEOUT`.
- API does not return an unhandled `500`.

Verified on 2026-05-03 with Docker Compose:

```json
{
  "status": 503,
  "body": {
    "error": {
      "code": "MODEL_UNAVAILABLE",
      "message": "model server is temporarily unavailable"
    }
  }
}
```

## Redis Down

Run:

```bash
scripts/failure_redis_down.sh
```

Expected result:

- `/ready` reports Redis as unavailable when strict readiness is enabled.
- Cache calls bypass failures.
- Rate limit checks fail closed with `RATE_LIMITER_UNAVAILABLE`.

Verified on 2026-05-03 with Docker Compose:

```json
{
  "status": "not_ready",
  "checks": {
    "database": "ok",
    "redis": "unavailable",
    "model_server": "ok"
  }
}
```

## DB Down

Run:

```bash
scripts/failure_db_down.sh
```

Expected result:

- `/health` remains process-level `ok`.
- `/ready` reports database unavailable.
- DB-backed `/v1/*` routes return `503 DATABASE_UNAVAILABLE`.

Verified on 2026-05-03 with Docker Compose:

```json
{
  "status": "not_ready",
  "checks": {
    "database": "unavailable",
    "redis": "ok",
    "model_server": "ok"
  }
}
```
