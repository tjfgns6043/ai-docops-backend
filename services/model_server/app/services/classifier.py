"""Prototype embedding classifier."""

from ..schemas.model import ClassificationLabel, PredictionItem
from .embedding_model import EmbeddingModel, cosine_similarity


class PrototypeClassifier:
    """Classify text using label description embeddings."""

    def __init__(self, model: EmbeddingModel) -> None:
        self.model = model

    def classify(
        self,
        text: str,
        labels: list[ClassificationLabel],
        top_k: int,
    ) -> list[PredictionItem]:
        """Return top labels by cosine similarity."""
        text_embedding = self.model.encode([text], normalize=True)[0]
        label_embeddings = self.model.encode(
            [label.description for label in labels],
            normalize=True,
        )

        predictions: list[PredictionItem] = []
        for label, embedding in zip(labels, label_embeddings, strict=True):
            raw_score = cosine_similarity(text_embedding, embedding)
            score = max(0.0, min(1.0, (raw_score + 1.0) / 2.0))
            predictions.append(PredictionItem(label=label.name, score=round(score, 6)))

        return sorted(predictions, key=lambda item: item.score, reverse=True)[:top_k]
