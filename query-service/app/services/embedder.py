from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed(text: str) -> list[float]:
    """Generate a 384-dimensional embedding vector for the given text."""
    model = _get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return [float(x) for x in vector]
