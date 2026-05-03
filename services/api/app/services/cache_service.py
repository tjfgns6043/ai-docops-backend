"""Redis cache helpers."""

import json
from dataclasses import dataclass
from time import perf_counter

from libs.common.hashing import sha256_hex

from ..core.config import Settings

try:
    from redis.asyncio import Redis
except ModuleNotFoundError:  # pragma: no cover
    Redis = None  # type: ignore[assignment]


def build_cache_key(
    env: str,
    tenant_id: str,
    operation: str,
    model_version: str,
    preprocess_version: str,
    input_hash: str,
) -> str:
    """Build a tenant-safe cache key."""
    return (
        f"ai-docops:{env}:{tenant_id}:{operation}:"
        f"{model_version}:{preprocess_version}:{input_hash}"
    )


def hash_payload(payload: object) -> str:
    """Hash a JSON-serializable payload."""
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256_hex(encoded)


@dataclass
class CacheResult:
    """Cache result with elapsed time."""

    value: dict[str, object] | None
    elapsed_ms: float


class CacheService:
    """Small Redis cache wrapper that safely bypasses cache failures."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._redis = Redis.from_url(settings.redis_url, decode_responses=True) if Redis else None

    async def get_json(self, key: str) -> CacheResult:
        """Get a JSON value. Cache failures are treated as misses."""
        started_at = perf_counter()
        if self._redis is None:
            return CacheResult(None, 0.0)
        try:
            raw = await self._redis.get(key)
        except Exception:
            return CacheResult(None, (perf_counter() - started_at) * 1000)
        if raw is None:
            return CacheResult(None, (perf_counter() - started_at) * 1000)
        return CacheResult(json.loads(raw), (perf_counter() - started_at) * 1000)

    async def set_json(self, key: str, value: dict[str, object], ttl_seconds: int) -> None:
        """Set a JSON value. Cache failures are ignored."""
        if self._redis is None:
            return
        try:
            await self._redis.set(key, json.dumps(value, ensure_ascii=False), ex=ttl_seconds)
        except Exception:
            return
