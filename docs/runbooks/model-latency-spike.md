# Model Latency Spike Runbook

1. Check model server `/ready`.
2. Inspect Prometheus `model_request_duration_seconds`.
3. Check worker queue and API p95 latency.
4. Confirm whether the first request is cold model loading.
5. Restart only `model-server` if the process is unhealthy.
