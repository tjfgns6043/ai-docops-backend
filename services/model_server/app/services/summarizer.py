"""Extractive summarizer."""

from .embedding_model import EmbeddingModel, cosine_similarity, normalize_vector
from .text_processing import split_sentences


def mean_vector(vectors: list[list[float]]) -> list[float]:
    """Return the centroid vector."""
    if not vectors:
        return []
    dimension = len(vectors[0])
    centroid = [0.0] * dimension
    for vector in vectors:
        for index, value in enumerate(vector):
            centroid[index] += value
    return normalize_vector([value / len(vectors) for value in centroid])


def select_top_non_duplicate(
    scored_sentences: list[tuple[int, float, str]],
    max_sentences: int,
) -> list[tuple[int, float, str]]:
    """Select top sentences while removing exact normalized duplicates."""
    selected: list[tuple[int, float, str]] = []
    seen: set[str] = set()
    for item in sorted(scored_sentences, key=lambda value: value[1], reverse=True):
        normalized = item[2].casefold().strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        selected.append(item)
        if len(selected) >= max_sentences:
            break
    return selected


class ExtractiveSummarizer:
    """Embedding-centroid extractive summarizer."""

    def __init__(self, model: EmbeddingModel) -> None:
        self.model = model

    def summarize(self, text: str, max_sentences: int) -> list[str]:
        """Return selected summary sentences in original order."""
        sentences = split_sentences(text)
        if len(sentences) <= max_sentences:
            return sentences

        embeddings = self.model.encode(sentences, normalize=True)
        centroid = mean_vector(embeddings)
        scored: list[tuple[int, float, str]] = []
        for index, embedding in enumerate(embeddings):
            position_bonus = 0.05 if index < 3 else 0.0
            score = cosine_similarity(embedding, centroid) + position_bonus
            scored.append((index, score, sentences[index]))

        selected = select_top_non_duplicate(scored, max_sentences)
        return [sentence for _, _, sentence in sorted(selected, key=lambda item: item[0])]
