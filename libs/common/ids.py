"""ID helpers."""

from uuid import UUID, uuid4


def new_uuid() -> UUID:
    """Create a UUID primary key value."""
    return uuid4()


def new_request_id() -> str:
    """Create a public request ID."""
    return f"req_{uuid4().hex}"
