from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_sentence_transformers():
    """Mock SentenceTransformer to avoid downloading model in tests."""
    with patch("app.services.embedder.SentenceTransformer") as mock_cls:
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.1] * 384
        mock_cls.return_value = mock_model
        # Reset the singleton so the mock is used
        import app.services.embedder as embedder_module
        embedder_module._model = None
        yield mock_cls
        embedder_module._model = None


def test_embedding_returns_correct_dimension():
    from app.services.embedder import embed
    vector = embed("test query")
    assert len(vector) == 384


def test_embedding_is_deterministic():
    from app.services.embedder import embed
    v1 = embed("same query")
    v2 = embed("same query")
    assert v1 == v2


def test_embedding_returns_list_of_floats():
    from app.services.embedder import embed
    vector = embed("test")
    assert isinstance(vector, list)
    assert all(isinstance(x, float) for x in vector)
