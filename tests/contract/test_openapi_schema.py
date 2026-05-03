from services.api.app.main import create_app


def test_openapi_contains_core_routes() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]

    for path in [
        "/v1/documents",
        "/v1/documents/{document_id}",
        "/v1/summaries",
        "/v1/summary-jobs",
        "/v1/predictions",
        "/v1/search",
        "/v1/rag/answers",
        "/v1/jobs/{job_id}",
    ]:
        assert path in paths
