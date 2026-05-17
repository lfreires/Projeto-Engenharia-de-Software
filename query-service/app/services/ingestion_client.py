import httpx

from app.config import settings


def normalize_ingestion_chunks(chunks: list[dict]) -> list[dict]:
    normalized = []
    for chunk in chunks:
        normalized.append(
            {
                "document_id": chunk["document_id"],
                "project_id": chunk["project_id"],
                "material_id": chunk["material_id"],
                "file_name": chunk["file_name"],
                "location": chunk.get("location")
                or f"{chunk['file_name']}#chunk-{chunk['chunk_index']}",
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "@search.score": chunk["score"],
            }
        )
    return normalized


async def search_ingestion(project_id: str, query: str, top_k: int) -> list[dict]:
    url = f"{settings.ingestion_service_url.rstrip('/')}/api/v1/ingestion/search"
    headers = {"Authorization": f"Bearer {settings.internal_service_token}"}
    payload = {"project_id": project_id, "query": query, "top_k": top_k}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

    return normalize_ingestion_chunks(response.json()["chunks"])
