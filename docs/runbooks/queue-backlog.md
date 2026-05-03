# Queue Backlog Runbook

1. Check `jobs` rows by tenant and status.
2. Confirm `worker` is running with `docker compose ps worker`.
3. Inspect worker logs with `docker compose logs worker`.
4. Reduce producer traffic if queue depth keeps growing.
5. Increase worker concurrency only after model server latency is stable.
