from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from app.config import settings

_client: SearchClient | None = None


def _get_client() -> SearchClient:
    global _client
    if _client is None:
        _client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_key),
        )
    return _client


def retrieve(embedding: list[float], project_id: str, top_k: int = settings.top_k) -> list[dict]:
    """Search Azure AI Search for the top_k most relevant chunks for project_id."""
    client = _get_client()

    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=f"project_id eq '{project_id}'",
        select=["document_id", "file_name", "chunk_index", "chunk_text", "project_id"],
        top=top_k,
    )

    chunks = []
    for result in results:
        chunks.append(
            {
                "document_id": result.get("document_id", ""),
                "file_name": result.get("file_name", ""),
                "chunk_index": result.get("chunk_index", 0),
                "chunk_text": result.get("chunk_text", ""),
                "@search.score": result.get("@search.score", 0.0),
            }
        )
    return chunks
