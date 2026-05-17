# PRD

## Responsibility

Receive documents, generate chunks/embeddings, maintain the vector index, and
serve search results to query-service. `embedder.py` and `retriever.py` live in
this service.

## Data

Target stores:

- Azure Blob Storage for files/chunks.
- Azure AI Search free tier as vector DB.

Domain IDs are `document_id`, `project_id`, `material_id`, and `chunk_index`.
