"""Development seed data."""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TENANT_A_ID = UUID("00000000-0000-0000-0000-00000000000a")
OWNER_A_ID = UUID("00000000-0000-0000-0000-0000000000aa")
DEV_API_KEY = "ak_dev_tenant_a_123456"


async def seed() -> None:
    """Seed tenant-a and a hashed development API key."""
    from libs.common.hashing import hash_api_key
    from services.api.app.db.models import ApiKey, Tenant
    from services.api.app.db.session import make_session_factory

    session_factory = make_session_factory()
    async with session_factory() as session:
        await session.execute(
            insert(Tenant)
            .values(id=TENANT_A_ID, name="tenant-a", status="active")
            .on_conflict_do_nothing(index_elements=[Tenant.id]),
        )
        await session.execute(
            insert(ApiKey)
            .values(
                tenant_id=TENANT_A_ID,
                owner_id=OWNER_A_ID,
                key_hash=hash_api_key(DEV_API_KEY),
                scopes=[
                    "documents:write",
                    "documents:read",
                    "summaries:write",
                    "predictions:write",
                    "search:read",
                    "jobs:read",
                ],
                status="active",
            )
            .on_conflict_do_nothing(index_elements=[ApiKey.key_hash]),
        )
        await session.commit()


def main() -> None:
    """Seed development data."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
