# DB Unavailable Runbook

1. Check `/ready` and confirm `database: unavailable`.
2. Check `docker compose ps postgres`.
3. Inspect logs with `docker compose logs postgres`.
4. Restart locally with `docker compose restart postgres`.
5. Re-run `make migrate` if schema state is uncertain.
