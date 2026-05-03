"""Model server request and response schemas."""

from pydantic import BaseModel, Field, field_validator


class EmbedRequest(BaseModel):
    """Embedding request."""

    texts: list[str] = Field(min_length=1, max_length=128)
    normalize: bool = True

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, texts: list[str]) -> list[str]:
        """Reject empty texts."""
        for text in texts:
            if not text.strip():
                raise ValueError("texts must not contain blank values")
        return texts


class EmbedResponse(BaseModel):
    """Embedding response."""

    model_version: str
    dimension: int
    embeddings: list[list[float]]
    elapsed_ms: float


class SummarizeExtractiveRequest(BaseModel):
    """Extractive summary request."""

    text: str = Field(min_length=1, max_length=100_000)
    max_sentences: int = Field(default=3, ge=1, le=10)
    language: str = Field(default="mixed", pattern="^(ko|en|mixed)$")


class SummarizeExtractiveResponse(BaseModel):
    """Extractive summary response."""

    model_version: str
    preprocess_version: str
    summary: str
    sentences: list[str]
    elapsed_ms: float


class ClassificationLabel(BaseModel):
    """Prototype classification label."""

    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)


class ClassifyPrototypeRequest(BaseModel):
    """Prototype classification request."""

    text: str = Field(min_length=1, max_length=20_000)
    labels: list[ClassificationLabel] = Field(min_length=1, max_length=50)
    top_k: int = Field(default=3, ge=1, le=10)


class PredictionItem(BaseModel):
    """One classification result."""

    label: str
    score: float = Field(ge=0.0, le=1.0)


class ClassifyPrototypeResponse(BaseModel):
    """Prototype classification response."""

    model_version: str
    predictions: list[PredictionItem]
    elapsed_ms: float
