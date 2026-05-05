import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest, ChatResponse, SourceItem


def test_chat_request_missing_project_id_raises():
    with pytest.raises(ValidationError):
        ChatRequest(session_id="s1", message="hello")


def test_chat_request_missing_session_id_raises():
    with pytest.raises(ValidationError):
        ChatRequest(project_id="p1", message="hello")


def test_chat_request_message_too_long_raises():
    with pytest.raises(ValidationError):
        ChatRequest(project_id="p1", session_id="s1", message="x" * 2001)


def test_chat_request_empty_message_raises():
    with pytest.raises(ValidationError):
        ChatRequest(project_id="p1", session_id="s1", message="")


def test_chat_request_valid():
    req = ChatRequest(project_id="p1", session_id="s1", message="hello")
    assert req.top_k == 5  # default


def test_chat_request_custom_top_k():
    req = ChatRequest(project_id="p1", session_id="s1", message="hello", top_k=10)
    assert req.top_k == 10


def test_chat_response_has_required_fields():
    source = SourceItem(document_id="d1", file_name="file.pdf", chunk_index=0, score=0.9)
    resp = ChatResponse(
        session_id="s1",
        answer="resposta",
        model_used="llama-3.3-70b-versatile",
        sources=[source],
        latency_ms=500,
    )
    assert resp.answer == "resposta"
    assert resp.session_id == "s1"
    assert resp.model_used == "llama-3.3-70b-versatile"
    assert len(resp.sources) == 1
    assert resp.latency_ms == 500
