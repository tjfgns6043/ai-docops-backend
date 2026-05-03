from services.model_server.app.core.config import Settings
from services.model_server.app.schemas.model import ClassificationLabel
from services.model_server.app.services.classifier import PrototypeClassifier
from services.model_server.app.services.embedding_model import EmbeddingModel


def test_classification_returns_top_k_and_score_range() -> None:
    classifier = PrototypeClassifier(EmbeddingModel(Settings(allow_model_fallback=True)))

    predictions = classifier.classify(
        "API latency and database cache behavior",
        [
            ClassificationLabel(name="backend", description="API database cache server"),
            ClassificationLabel(name="security", description="authentication secrets encryption"),
            ClassificationLabel(name="mlops", description="model deployment monitoring"),
        ],
        top_k=2,
    )

    assert len(predictions) == 2
    assert all(0.0 <= prediction.score <= 1.0 for prediction in predictions)
