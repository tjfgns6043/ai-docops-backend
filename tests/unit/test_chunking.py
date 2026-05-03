from services.model_server.app.services.text_processing import chunk_text, split_sentences


def test_sentence_splitting_supports_mixed_punctuation() -> None:
    text = "첫 문장입니다. Second sentence! 마지막 문장?"

    assert split_sentences(text) == ["첫 문장입니다.", "Second sentence!", "마지막 문장?"]


def test_chunking_is_deterministic() -> None:
    text = "A first sentence. A second sentence. A third sentence."

    assert chunk_text(text, max_chars=25) == chunk_text(text, max_chars=25)
