"""Text processing helpers."""

import re

PREPROCESS_VERSION = "text-preprocess-v1"
SENTENCE_PATTERN = re.compile(r"[^.!?。！？\n]+[.!?。！？]?")


def normalize_text(text: str) -> str:
    """Normalize text without changing meaning."""
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    """Split Korean, English, and mixed text into rough sentences."""
    normalized = normalize_text(text)
    if not normalized:
        return []

    sentences = [match.group(0).strip() for match in SENTENCE_PATTERN.finditer(normalized)]
    return [sentence for sentence in sentences if sentence]


def chunk_text(text: str, max_chars: int = 1200, overlap_sentences: int = 1) -> list[str]:
    """Chunk text deterministically by sentence with light overlap."""
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        sentence_len = len(sentence)
        if current and current_len + sentence_len + 1 > max_chars:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_len = sum(len(item) + 1 for item in current)
        current.append(sentence)
        current_len += sentence_len + 1

    if current:
        chunks.append(" ".join(current))
    return chunks


def estimate_tokens(text: str) -> int:
    """Estimate tokens for storage metadata."""
    return max(1, len(text) // 4)
