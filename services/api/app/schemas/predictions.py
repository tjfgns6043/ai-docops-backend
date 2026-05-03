"""Prediction API schemas."""

from pydantic import BaseModel, Field


class PredictionLabel(BaseModel):
    """Classification label."""

    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)


class PredictionRequest(BaseModel):
    """Prototype classification request."""

    text: str = Field(min_length=1, max_length=20_000)
    labels: list[PredictionLabel] = Field(min_length=1, max_length=50)
    top_k: int = Field(default=3, ge=1, le=10)


class PredictionItem(BaseModel):
    """One prediction."""

    label: str
    score: float = Field(ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    """Prediction response."""

    request_id: str
    model_version: str
    predictions: list[PredictionItem]
    elapsed_ms: float
    cached: bool
