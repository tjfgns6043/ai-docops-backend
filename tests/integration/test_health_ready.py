from fastapi.testclient import TestClient

from services.api.app.main import create_app


def test_health_returns_api_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api"}


def test_ready_returns_placeholder_checks() -> None:
    client = TestClient(create_app())

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "api", "checks": {}}


def test_request_id_is_echoed() -> None:
    client = TestClient(create_app())

    response = client.get("/health", headers={"X-Request-ID": "client-request-id"})

    assert response.headers["X-Request-ID"] == "client-request-id"
    assert "X-Response-Time-Ms" in response.headers


def test_not_found_uses_error_envelope() -> None:
    client = TestClient(create_app())

    response = client.get("/missing", headers={"X-Request-ID": "req_test"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Not Found",
            "request_id": "req_test",
        }
    }


def test_metrics_placeholder_is_prometheus_text() -> None:
    client = TestClient(create_app())

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "ai_docops_build_info" in response.text
