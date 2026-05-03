from uuid import UUID

from services.api.app.services.rate_limit_service import rate_limit_key


def test_rate_limit_key_includes_tenant_operation_and_window() -> None:
    tenant_id = UUID("00000000-0000-0000-0000-00000000000a")

    assert rate_limit_key(tenant_id, "summaries", 123) == (
        "rate:00000000-0000-0000-0000-00000000000a:summaries:123"
    )
