from app.config import settings
from app.schemas.chat import HistoryTurn, SourceItem

_SYSTEM_PROMPT = (
    "Você é um assistente especializado em documentação de projetos de software. "
    "Responda com base exclusivamente nos trechos de documentação fornecidos no contexto. "
    "Se a informação não estiver no contexto, diga que não encontrou nos documentos indexados. "
    "Seja objetivo, claro e cite as fontes quando relevante."
)

# Rough approximation: 1 token ≈ 4 characters
_CHARS_PER_TOKEN = 4


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def _estimate_tokens(text: str) -> int:
    return len(text) // _CHARS_PER_TOKEN


def build_messages(
    query: str,
    context_chunks: list[dict],
    history: list[HistoryTurn],
    max_context_tokens: int = settings.max_context_tokens,
    max_history_turns: int = settings.max_history_turns,
) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]

    # Add last N turns of history (each turn = 1 HistoryTurn object, so N turns = N messages)
    recent = history[-(max_history_turns):]
    for turn in recent:
        messages.append({"role": turn.role, "content": turn.content})

    # Build context block from chunks, respecting token limit
    context_parts: list[str] = []
    used_tokens = 0
    for chunk in context_chunks:
        text = chunk.get("chunk_text", "")
        tokens = _estimate_tokens(text)
        if used_tokens + tokens > max_context_tokens:
            # Truncate the chunk to fit
            remaining_chars = (max_context_tokens - used_tokens) * _CHARS_PER_TOKEN
            text = text[:remaining_chars]
            context_parts.append(f"[{chunk.get('file_name', 'doc')}]\n{text}")
            break
        context_parts.append(f"[{chunk.get('file_name', 'doc')}]\n{text}")
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
                file_name=result.get("file_name", ""),
                chunk_index=result.get("chunk_index", 0),
                score=result.get("@search.score", 0.0),
            )
        )
    return sources
