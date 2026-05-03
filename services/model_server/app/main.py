"""Model server entrypoint."""

from fastapi import FastAPI

from .core.config import get_settings
from .core.logging import configure_logging
from .core.metrics import mark_model_loaded, metrics, model_timer
from .schemas.model import (
    ClassifyPrototypeRequest,
    ClassifyPrototypeResponse,
    EmbedRequest,
    EmbedResponse,
    SummarizeExtractiveRequest,
    SummarizeExtractiveResponse,
)
from .services.classifier import PrototypeClassifier
from .services.embedding_model import EmbeddingModel
from .services.summarizer import ExtractiveSummarizer


def create_app() -> FastAPI:
    """Create the model server app."""
    settings = get_settings()
    configure_logging(settings)
    embedding_model = EmbeddingModel(settings)
    summarizer = ExtractiveSummarizer(embedding_model)
    classifier = PrototypeClassifier(embedding_model)

    app = FastAPI(
        title="AI DocOps Model Server",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.state.settings = settings
    app.state.embedding_model = embedding_model
    app.state.summarizer = summarizer
    app.state.classifier = classifier

    @app.on_event("startup")
    async def load_model() -> None:
        embedding_model.load()
        mark_model_loaded(settings.model_version, embedding_model.loaded)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/ready")
    async def ready() -> dict[str, object]:
        return {
            "status": "ready" if embedding_model.loaded else "not_ready",
            "service": settings.service_name,
            "model_loaded": embedding_model.loaded,
            "fallback": embedding_model.using_fallback,
        }

    @app.post("/embed", response_model=EmbedResponse)
    async def embed(payload: EmbedRequest) -> EmbedResponse:
        with model_timer("embed", settings.model_version, len(payload.texts)) as timer:
            embeddings = embedding_model.encode(payload.texts, normalize=payload.normalize)
        return EmbedResponse(
            model_version=settings.model_version,
            dimension=settings.embedding_dimension,
            embeddings=embeddings,
            elapsed_ms=timer.elapsed_ms,
        )

    @app.post("/summarize-extractive", response_model=SummarizeExtractiveResponse)
    async def summarize(payload: SummarizeExtractiveRequest) -> SummarizeExtractiveResponse:
        with model_timer("summarize_extractive", settings.model_version) as timer:
            sentences = summarizer.summarize(payload.text, payload.max_sentences)
        return SummarizeExtractiveResponse(
            model_version=settings.model_version,
            preprocess_version=settings.preprocess_version,
            summary=" ".join(sentences),
            sentences=sentences,
            elapsed_ms=timer.elapsed_ms,
        )

    @app.post("/classify-prototype", response_model=ClassifyPrototypeResponse)
    async def classify(payload: ClassifyPrototypeRequest) -> ClassifyPrototypeResponse:
        with model_timer(
            "classify_prototype",
            settings.model_version,
            len(payload.labels),
        ) as timer:
            predictions = classifier.classify(payload.text, payload.labels, payload.top_k)
        return ClassifyPrototypeResponse(
            model_version=settings.model_version,
            predictions=predictions,
            elapsed_ms=timer.elapsed_ms,
        )

    app.add_api_route("/metrics", metrics, methods=["GET"], include_in_schema=False)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.model_server.app.main:app", host="0.0.0.0", port=9000, reload=False)
