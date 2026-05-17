from app.services.ingestion_client import normalize_ingestion_chunks


def test_normalize_ingestion_chunks_preserves_contract_fields():
    chunks = normalize_ingestion_chunks(
        [
            {
                "document_id": "doc-1",
                "project_id": "proj-demo",
                "material_id": "mat-1",
                "file_name": "architecture.pdf",
                "location": "architecture.pdf#chunk-2",
                "chunk_index": 2,
                "chunk_text": "Relevant text",
                "score": 0.87,
            }
        ]
    )

    assert chunks == [
        {
            "document_id": "doc-1",
            "project_id": "proj-demo",
            "material_id": "mat-1",
            "file_name": "architecture.pdf",
            "location": "architecture.pdf#chunk-2",
            "chunk_index": 2,
            "chunk_text": "Relevant text",
            "@search.score": 0.87,
        }
    ]
