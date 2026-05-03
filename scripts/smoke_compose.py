"""End-to-end smoke test for a running AI DocOps stack."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any
from uuid import uuid4

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "ak_dev_tenant_a_123456")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("SMOKE_REQUEST_TIMEOUT_SECONDS", "30"))
JOB_TIMEOUT_SECONDS = float(os.getenv("SMOKE_JOB_TIMEOUT_SECONDS", "120"))


def request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Call the API and return a JSON response."""
    headers = dict(extra_headers or {})
    if path.startswith("/v1"):
        headers.setdefault("X-API-Key", API_KEY)
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        f"{API_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise AssertionError(f"{method} {path} failed with {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise AssertionError(f"{method} {path} failed: {exc}") from exc
    return json.loads(body) if body else {}


def wait_ready(timeout_seconds: float = 120) -> dict[str, Any]:
    """Wait until the API reports strict readiness."""
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        try:
            body = request("GET", "/ready")
            if body.get("status") == "ready":
                return body
            last_error = json.dumps(body, sort_keys=True)
        except AssertionError as exc:
            last_error = str(exc)
        time.sleep(2)
    raise AssertionError(f"API was not ready before timeout: {last_error}")


def wait_job_completed(job_id: str) -> dict[str, Any]:
    """Poll a job until it completes or fails."""
    deadline = time.monotonic() + JOB_TIMEOUT_SECONDS
    last_status = "unknown"
    while time.monotonic() < deadline:
        body = request("GET", f"/v1/jobs/{job_id}")
        last_status = str(body.get("status"))
        if last_status == "completed":
            return body
        if last_status == "failed":
            raise AssertionError(f"job {job_id} failed: {json.dumps(body.get('error'))}")
        time.sleep(2)
    raise AssertionError(f"job {job_id} did not complete; last_status={last_status}")


def assert_true(condition: bool, message: str) -> None:
    """Raise an assertion with a readable message."""
    if not condition:
        raise AssertionError(message)


def main() -> None:
    """Run the smoke test."""
    ready = wait_ready()
    suffix = uuid4().hex[:12]

    summary_payload = {
        "text": (
            f"Smoke run {suffix}. FastAPI accepts tenant scoped requests. "
            "The model server creates sentence embeddings. Redis stores cache entries. "
            "PostgreSQL stores indexed document chunks."
        ),
        "max_sentences": 2,
        "language": "en",
    }
    first_summary = request("POST", "/v1/summaries", summary_payload)
    second_summary = request("POST", "/v1/summaries", summary_payload)
    assert_true(first_summary["summary"], "summary response was empty")
    assert_true(second_summary["cached"] is True, "second summary request was not cached")

    prediction = request(
        "POST",
        "/v1/predictions",
        {
            "text": "API latency, Redis cache, and database queries",
            "labels": [
                {"name": "backend", "description": "API database cache server development"},
                {"name": "security", "description": "authentication secrets encryption"},
                {"name": "mlops", "description": "model deployment monitoring operations"},
            ],
            "top_k": 2,
        },
    )
    assert_true(len(prediction["predictions"]) == 2, "prediction top_k was not respected")

    document = request(
        "POST",
        "/v1/documents",
        {
            "title": f"Smoke runbook {suffix}",
            "text": (
                "When model latency increases, check p95 latency, queue depth, traces, "
                "recent deployments, Redis health, and database query latency. "
                "Document chunks are embedded for tenant scoped semantic search."
            ),
            "language": "en",
            "metadata": {"source": "smoke-compose"},
        },
    )
    document_id = document["document_id"]
    job = request(
        "POST",
        f"/v1/documents/{document_id}/index-jobs",
        extra_headers={"Idempotency-Key": f"smoke-index-{suffix}"},
    )
    completed_job = wait_job_completed(job["job_id"])

    search = request(
        "POST",
        "/v1/search",
        {
            "query": "What should I check when model latency increases?",
            "top_k": 3,
            "document_ids": [document_id],
        },
    )
    assert_true(len(search["results"]) >= 1, "search returned no results")

    rag = request(
        "POST",
        "/v1/rag/answers",
        {
            "question": "What should I check when model latency increases?",
            "top_k": 3,
            "max_answer_sentences": 2,
        },
    )
    assert_true(rag["answer_type"] == "extractive", "RAG answer was not extractive")
    assert_true(len(rag["citations"]) >= 1, "RAG response had no citations")

    print(
        json.dumps(
            {
                "status": "SMOKE_OK",
                "ready": ready["checks"],
                "document_id": document_id,
                "index_job_id": completed_job["job_id"],
                "summary_cached": second_summary["cached"],
                "prediction_labels": [item["label"] for item in prediction["predictions"]],
                "search_results": len(search["results"]),
                "rag_citations": len(rag["citations"]),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
