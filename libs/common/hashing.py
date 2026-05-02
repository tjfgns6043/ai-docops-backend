"""Hashing helpers."""

from hashlib import sha256


def sha256_hex(value: str) -> str:
    """Return a deterministic SHA-256 hex digest for non-secret cache inputs."""
    return sha256(value.encode("utf-8")).hexdigest()


def hash_api_key(api_key: str) -> str:
    """Hash an API key before persistence or lookup."""
    return sha256_hex(api_key)
