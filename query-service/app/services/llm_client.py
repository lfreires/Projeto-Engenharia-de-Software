from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openai import OpenAI
from pydantic import SecretStr

from app.config import settings

ChatGroq: Any
try:
    from langchain_groq import ChatGroq as ChatGroq
except ImportError:  # pragma: no cover - dependency is installed in production images.
    ChatGroq = None


PRIMARY_MODEL = settings.primary_llm_model
FALLBACK_MODEL = settings.fallback_llm_model


def _to_langchain_messages(messages: Sequence[dict[str, Any]]) -> list[BaseMessage]:
    converted: list[BaseMessage] = []
    for message in messages:
        role = message.get("role")
        content = str(message.get("content", ""))
        if role == "system":
            converted.append(SystemMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
        else:
            converted.append(HumanMessage(content=content))
    return converted


class GroqLangChainClient:
    def __init__(self, api_key: str, temperature: float = 0, max_tokens: int = 1024) -> None:
        self._api_key = api_key
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._openai_fallback = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

    def invoke(self, messages: Sequence[dict[str, Any]], model: str) -> str:
        if ChatGroq is not None:
            llm = ChatGroq(
                model=model,
                api_key=SecretStr(self._api_key),
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            langchain_response = llm.invoke(_to_langchain_messages(messages))
            return str(langchain_response.content or "")

        openai_response = self._openai_fallback.chat.completions.create(
            model=model,
            messages=list(messages),  # type: ignore[arg-type]
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return openai_response.choices[0].message.content or ""


client = GroqLangChainClient(api_key=settings.groq_api_key)


def chat_completion(messages: list[dict], model: str = PRIMARY_MODEL) -> tuple[str, str]:
    try:
        return client.invoke(messages, model=model), model
    except Exception as exc:
        if "429" in str(exc) and model == PRIMARY_MODEL:
            return chat_completion(messages, model=FALLBACK_MODEL)
        raise
