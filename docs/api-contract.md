# API Contract

All `/v1/*` routes require:

```http
X-API-Key: ak_dev_tenant_a_123456
```

Errors use:

```json
{
  "error": {
    "code": "MODEL_UNAVAILABLE",
    "message": "model server is temporarily unavailable",
    "request_id": "req_..."
  }
}
```

Implemented route groups:

- `POST /v1/documents`
- `GET /v1/documents/{document_id}`
- `POST /v1/documents/{document_id}/index-jobs`
- `POST /v1/summaries`
- `POST /v1/summary-jobs`
- `GET /v1/jobs/{job_id}`
- `GET /v1/summary-jobs/{job_id}`
- `POST /v1/predictions`
- `POST /v1/search`
- `POST /v1/rag/answers`

Run `make openapi` to export `docs/openapi.json`.
