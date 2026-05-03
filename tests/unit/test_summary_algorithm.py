from services.model_server.app.core.config import Settings
from services.model_server.app.services.embedding_model import EmbeddingModel
from services.model_server.app.services.summarizer import ExtractiveSummarizer


def test_summary_respects_max_sentences_and_original_order() -> None:
    model = EmbeddingModel(Settings(allow_model_fallback=True))
    summarizer = ExtractiveSummarizer(model)
    text = "Alpha systems run APIs. Beta systems run workers. Gamma systems store data."

    sentences = summarizer.summarize(text, max_sentences=2)

    assert len(sentences) <= 2
    positions = [text.index(sentence) for sentence in sentences]
    assert positions == sorted(positions)
