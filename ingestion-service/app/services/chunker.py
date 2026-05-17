class TextChunker:
    def __init__(self, max_words: int) -> None:
        self._max_words = max_words

    def split(self, content: str, max_words: int | None = None) -> list[str]:
        limit = max_words or self._max_words
        words = content.split()
        return [" ".join(words[index : index + limit]) for index in range(0, len(words), limit)]
