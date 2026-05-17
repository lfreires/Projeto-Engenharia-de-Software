from app.schemas.chat import HistoryTurn
from app.services.prompt_builder import build_messages, build_system_prompt, format_sources


def test_build_system_prompt_returns_string():
    prompt = build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_prompt_includes_context():
    chunks = [
        {
            "chunk_text": "Microservices architecture uses Docker.",
            "file_name": "arch.pdf",
            "chunk_index": 0,
        },
    ]
    messages = build_messages(query="What is the architecture?", context_chunks=chunks, history=[])
    # context must appear somewhere in the messages
    full_text = " ".join(m["content"] for m in messages)
    assert "Microservices architecture" in full_text


def test_build_prompt_respects_token_limit():
    # Generate a large chunk that would exceed 2000 tokens
    large_chunk = {"chunk_text": "word " * 3000, "file_name": "big.pdf", "chunk_index": 0}
    messages = build_messages(query="summary", context_chunks=[large_chunk], history=[])
    # Context in user message must be truncated — total words in content < 3000
    full_text = " ".join(m["content"] for m in messages if m["role"] == "user")
    # A very rough proxy: 2000 tokens ≈ 1500 words
    assert len(full_text.split()) < 3000


def test_build_prompt_includes_query():
    messages = build_messages(query="What is PIX?", context_chunks=[], history=[])
    user_messages = [m for m in messages if m["role"] == "user"]
    assert any("What is PIX?" in m["content"] for m in user_messages)


def test_chat_history_max_turns():
    history = [
        HistoryTurn(role="user", content=f"msg {i}")
        if i % 2 == 0
        else HistoryTurn(role="assistant", content=f"resp {i}")
        for i in range(20)
    ]
    messages = build_messages(query="current question", context_chunks=[], history=history)
    # system prompt + max 5 turns (10 messages) + 1 user query = at most 12
    assert len(messages) <= 12


def test_format_sources_returns_list():
    search_results = [
        {"document_id": "d1", "file_name": "arch.pdf", "chunk_index": 0, "@search.score": 0.95},
        {"document_id": "d2", "file_name": "readme.md", "chunk_index": 1, "@search.score": 0.80},
    ]
    sources = format_sources(search_results)
    assert isinstance(sources, list)
    assert len(sources) == 2
    assert sources[0].document_id == "d1"
    assert sources[0].score == 0.95


def test_format_sources_empty_list():
    assert format_sources([]) == []
