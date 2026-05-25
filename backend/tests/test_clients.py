import pytest
from langchain_core.documents import Document

import app.rag as rag
from app.clients import GroqChatClient
from app.config import Settings
from app.schemas import SearchChunk


def test_gemini_embedding_adapter_prefixes_documents_and_queries(monkeypatch):
    class StubGemini:
        def __init__(self, **kwargs):
            assert kwargs["model"] == "gemini-embedding-2"
            assert kwargs["output_dimensionality"] == 768
            self.texts = []

        def embed_documents(self, texts):
            self.texts.extend(texts)
            return [[0.1] * 768 for _ in texts]

        def embed_query(self, text):
            self.texts.append(text)
            return [0.2] * 768

    monkeypatch.setattr(rag, "GoogleGenerativeAIEmbeddings", StubGemini)
    embeddings = rag.PrefixedGeminiEmbeddings(Settings(gemini_api_key="secret"))
    embeddings.embed_document_chunks(
        [Document(page_content="conteudo", metadata={"file_name": "design.pdf"})]
    )
    embeddings.embed_query("qual arquitetura?")
    assert embeddings._delegate.texts[0] == "title: design.pdf | text: conteudo"
    assert embeddings._delegate.texts[1] == "task: question answering | query: qual arquitetura?"


@pytest.mark.asyncio
async def test_groq_falls_back_after_rate_limit(monkeypatch):
    client = GroqChatClient(Settings(groq_api_key="secret"))
    models = []

    async def invoke(question, chunks, history, max_context_words, model):
        del question, chunks, history, max_context_words
        models.append(model)
        if len(models) == 1:
            error = RuntimeError("limit")
            error.status_code = 429
            raise error
        return "fallback"

    monkeypatch.setattr(client, "_invoke", invoke)
    answer, model = await client.complete(
        "ola",
        [
            SearchChunk(
                document_id="doc",
                project_id="proj",
                material_id="mat",
                file_name="readme.md",
                location="readme.md",
                chunk_index=0,
                chunk_text="texto",
                score=1,
            )
        ],
        [],
        100,
    )
    assert answer == "fallback"
    assert models == ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    assert model == "llama-3.1-8b-instant"
