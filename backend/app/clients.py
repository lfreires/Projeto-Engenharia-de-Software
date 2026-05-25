from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from app.config import Settings
from app.schemas import HistoryTurn, SearchChunk


class GroqChatClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Responda somente com base no contexto recuperado. "
                    "Quando apropriado, cite apenas o nome do arquivo entre colchetes. "
                    "Nao exponha indices, IDs internos ou nomes de chunks.",
                ),
                MessagesPlaceholder("history"),
                ("human", "Contexto:\n{context}\n\nPergunta: {question}"),
            ]
        )

    async def complete(
        self,
        question: str,
        chunks: list[SearchChunk],
        history: list[HistoryTurn],
        max_context_words: int,
    ) -> tuple[str, str]:
        try:
            answer = await self._invoke(
                question, chunks, history, max_context_words, self._settings.primary_llm_model
            )
            return answer, self._settings.primary_llm_model
        except Exception as exc:
            if not _is_rate_limit(exc):
                raise
            answer = await self._invoke(
                question, chunks, history, max_context_words, self._settings.fallback_llm_model
            )
            return answer, self._settings.fallback_llm_model

    async def _invoke(
        self,
        question: str,
        chunks: list[SearchChunk],
        history: list[HistoryTurn],
        max_context_words: int,
        model: str,
    ) -> str:
        if not self._settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required to answer chat requests.")
        context = "\n\n".join(f"[Fonte: {chunk.file_name}]\n{chunk.chunk_text}" for chunk in chunks)
        context = " ".join(context.split()[:max_context_words])
        prior_messages = [
            HumanMessage(content=turn.content)
            if turn.role == "user"
            else AIMessage(content=turn.content)
            for turn in history
        ]
        chat_model = ChatGroq(
            api_key=self._settings.groq_api_key,
            model=model,
            temperature=0,
            max_tokens=1024,
            timeout=60,
            max_retries=0,
        )
        chain = self._prompt | chat_model | StrOutputParser()
        return await chain.ainvoke(
            {"context": context, "question": question, "history": prior_messages}
        )


def _is_rate_limit(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None) == 429
