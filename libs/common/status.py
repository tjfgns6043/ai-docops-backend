"""Shared status constants."""

DOCUMENT_UPLOADED = "uploaded"
DOCUMENT_INDEXING = "indexing"
DOCUMENT_INDEXED = "indexed"
DOCUMENT_INDEX_FAILED = "index_failed"

JOB_QUEUED = "queued"
JOB_RUNNING = "running"
JOB_RETRYING = "retrying"
JOB_COMPLETED = "completed"
JOB_FAILED = "failed"
JOB_CANCELLED = "cancelled"

ALLOWED_JOB_TRANSITIONS = {
    JOB_QUEUED: {JOB_RUNNING, JOB_CANCELLED},
    JOB_RUNNING: {JOB_COMPLETED, JOB_RETRYING, JOB_FAILED},
    JOB_RETRYING: {JOB_RUNNING, JOB_FAILED},
    JOB_COMPLETED: set(),
    JOB_FAILED: set(),
    JOB_CANCELLED: set(),
}


def can_transition_job(from_status: str, to_status: str) -> bool:
    """Return whether a job status transition is allowed."""
    return to_status in ALLOWED_JOB_TRANSITIONS.get(from_status, set())
