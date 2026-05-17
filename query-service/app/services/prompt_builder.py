from app.config import settings
from app.schemas.chat import HistoryTurn, SourceItem

_SYSTEM_PROMPT = (
    "Voce e um assistente especializado em documentacao de projetos de software. "
    "Responda com base exclusivamente nos trechos fornecidos no contexto. "
    "Se a informacao nao estiver no contexto, diga que nao encontrou nos documentos indexados. "
    "Cite as fontes pelo nome do arquivo e chunk quando relevante. "
    "Nunca invente caminhos, arquivos ou fatos que nao aparecam no contexto."
)

_CHARS_PER_TOKEN = 4


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def _estimate_tokens(text: str) -> int:
    return len(text) // _CHARS_PER_TOKEN


def _chunk_location(chunk: dict) -> str:
    file_name = chunk.get("file_name", "doc")
    chunk_index = chunk.get("chunk_index", 0)
    return chunk.get("location") or f"{file_name}#chunk-{chunk_index}"


def build_messages(
    query: str,
    context_chunks: list[dict],
    history: list[HistoryTurn],
    max_context_tokens: int = settings.max_context_tokens,
    max_history_turns: int = settings.max_history_turns,
) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]

    recent = history[-max_history_turns:]
    for turn in recent:
        messages.append({"role": turn.role, "content": turn.content})

    context_parts: list[str] = []
    used_tokens = 0
    for chunk in context_chunks:
        text = chunk.get("chunk_text", "")
        tokens = _estimate_tokens(text)
        header = f"[Fonte: {_chunk_location(chunk)}]"

        if used_tokens + tokens > max_context_tokens:
            remaining_chars = (max_context_tokens - used_tokens) * _CHARS_PER_TOKEN
            context_parts.append(f"{header}\n{text[:remaining_chars]}")
            break

        context_parts.append(f"{header}\n{text}")
        used_tokens += tokens

    context_block = "\n\n".join(context_parts)
    if context_block:
        user_content = f"Contexto dos documentos:\n{context_block}\n\nPergunta: {query}"
    else:
        user_content = f"Pergunta: {query}"

    messages.append({"role": "user", "content": user_content})
    return messages


def format_sources(search_results: list[dict]) -> list[SourceItem]:
    sources = []
    for result in search_results:
        sources.append(
            SourceItem(
                document_id=result.get("document_id", ""),
                material_id=result.get("material_id"),
                file_name=result.get("file_name", ""),
                location=_chunk_location(result),
                chunk_index=result.get("chunk_index", 0),
                score=result.get("@search.score", 0.0),
            )
        )
    return sources
