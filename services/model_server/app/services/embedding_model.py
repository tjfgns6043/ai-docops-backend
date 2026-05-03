"""Embedding model wrapper."""

from hashlib import blake2b
from math import sqrt

from ..core.config import Settings


def normalize_vector(vector: list[float]) -> list[float]:
    """L2 normalize a vector."""
    norm = sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for normalized or unnormalized vectors."""
    left_norm = sqrt(sum(value * value for value in left)) or 1.0
    right_norm = sqrt(sum(value * value for value in right)) or 1.0
    return sum(a * b for a, b in zip(left, right, strict=False)) / (left_norm * right_norm)


class EmbeddingModel:
    """SentenceTransformer wrapper with deterministic fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_version = settings.model_version
        self.dimension = settings.embedding_dimension
        self._model: object | None = None
        self.loaded = False
        self.using_fallback = False

    def load(self) -> None:
        """Load the configured embedding model once."""
        if self.loaded:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.settings.model_name,
                device=self.settings.model_device,
            )
        except Exception as exc:
            if not self.settings.allow_model_fallback:
                msg = f"failed to load embedding model {self.settings.model_name}"
                raise RuntimeError(msg) from exc
            self._model = None
            self.using_fallback = True
        self.loaded = True

    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """Encode texts to vectors."""
        self.load()
        if self._model is not None:
            embeddings = self._model.encode(texts, normalize_embeddings=normalize)
            return [list(map(float, embedding)) for embedding in embeddings]
        return [self._fallback_embedding(text, normalize) for text in texts]

    def _fallback_embedding(self, text: str, normalize: bool) -> list[float]:
        vector = [0.0] * self.dimension
        words = text.lower().split() or [text.lower()]
        for position, word in enumerate(words):
            digest = blake2b(f"{position}:{word}".encode(), digest_size=32).digest()
            for idx, byte in enumerate(digest):
                vector[(idx * 17 + byte) % self.dimension] += (byte - 127.5) / 127.5
        return normalize_vector(vector) if normalize else vector
