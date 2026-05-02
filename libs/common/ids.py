"""ID helpers."""

from uuid import UUID, uuid4


def new_uuid() -> UUID:
    """Create a UUID primary key value."""
    return uuid4()
