from functools import lru_cache

from app.services.chat_service import ChatService
from app.services.feedback_service import InMemoryFeedbackStore
from app.services.session_service import InMemorySessionStore
from app.services.token_validator import TokenValidator


@lru_cache
def get_session_store() -> InMemorySessionStore:
    return InMemorySessionStore()


@lru_cache
def get_feedback_store() -> InMemoryFeedbackStore:
    return InMemoryFeedbackStore()


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(sessions=get_session_store())


@lru_cache
def get_token_validator() -> TokenValidator:
    return TokenValidator()
