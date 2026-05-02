"""API service entrypoint."""

from fastapi import FastAPI

from .api.routes_health import router as health_router
from .core.config import get_settings
from .core.errors import add_exception_handlers
from .core.logging import configure_logging
from .core.metrics import metrics
from .core.middleware import RequestIdMiddleware


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="AI DocOps Backend API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = settings

    app.add_middleware(RequestIdMiddleware)
    add_exception_handlers(app)
    app.include_router(health_router)
    app.add_api_route("/metrics", metrics, methods=["GET"], include_in_schema=False)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.api.app.main:app", host="0.0.0.0", port=8000, reload=False)
