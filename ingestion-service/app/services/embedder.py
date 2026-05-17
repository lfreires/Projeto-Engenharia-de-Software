def embed(text: str) -> list[float]:
    """Deterministic local placeholder for the migrated embedding boundary."""
    tokens = text.lower().split()
    return [float(len(tokens)), float(sum(len(token) for token in tokens))]
