"""API metrics placeholder."""

from fastapi.responses import PlainTextResponse


async def metrics() -> PlainTextResponse:
    """Return a Prometheus-compatible placeholder until real metrics are added."""
    return PlainTextResponse(
        "# HELP ai_docops_build_info Build information placeholder\n"
        "# TYPE ai_docops_build_info gauge\n"
        'ai_docops_build_info{service="api"} 1\n',
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
