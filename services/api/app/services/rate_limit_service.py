"""Redis rate limiting."""

from dataclasses import dataclass
from time import time
from uuid import UUID

from ..core.config import Settings

try:
    from redis.asyncio import Redis
except ModuleNotFoundError:  # pragma: no cover
    Redis = None  # type: ignore[assignment]


def rate_limit_key(tenant_id: UUID, operation: str, window_start_epoch: int) -> str:
    """Build a rate limit key."""
    return f"rate:{tenant_id}:{operation}:{window_start_epoch}"


@dataclass(frozen=True)
class RateLimitPolicy:
    """Rate limit policy."""

    operation: str
    limit: int


POLICIES = {
    "summaries": RateLimitPolicy("summaries", 60),
    "predictions": RateLimitPolicy("predictions", 120),
    "search": RateLimitPolicy("search", 120),
    "job_create": RateLimitPolicy("job_create", 30),
}


class RateLimitExceeded(Exception):
    """Raised when a tenant exceeds its rate limit."""


class RateLimiterUnavailable(Exception):
    """Raised when rate limiting cannot be checked."""


class RateLimitService:
    """Redis INCR/EXPIRE based rate limiter."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._redis = Redis.from_url(settings.redis_url, decode_responses=True) if Redis else None

    async def check(self, tenant_id: UUID, operation: str) -> None:
        """Check one tenant operation against the configured policy."""
        policy = POLICIES[operation]
        if self._redis is None:
            return

        now = int(time())
        window = self.settings.rate_limit_window_seconds
        window_start = now - (now % window)
        key = rate_limit_key(tenant_id, policy.operation, window_start)
        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, window)
        except Exception as exc:
            raise RateLimiterUnavailable from exc

        if count > policy.limit:
            raise RateLimitExceeded
