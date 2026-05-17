# docai-ingestion-service

Servico FastAPI responsavel por ingestao, chunking, embeddings e busca
documental. Este servico e o unico dono do indice vetorial e do armazenamento
de arquivos/chunks. O query-service nunca acessa AI Search diretamente.

## Arquitetura

```mermaid
flowchart LR
    Client[Frontend ou automacao] -->|POST /documents| API[ingestion router]
    Query[query-service] -->|POST /search| API
    API --> AUTH[TokenValidator]
    AUTH -->|opcional| Identity[identity-service]
    API --> SVC[IngestionService]
    SVC --> CHUNK[TextChunker]
    SVC --> EMB[Embedder]
    SVC --> IDX[DocumentIndex]
    IDX -->|prod| Blob[Azure Blob Storage]
    IDX -->|prod| Search[Azure AI Search Free]
    IDX -->|local| Memory[InMemoryDocumentIndex]
```

## Fluxo De Ingestao

```mermaid
sequenceDiagram
    participant Client
    participant Ingestion
    participant Chunker
    participant Index

    Client->>Ingestion: POST /documents
    Ingestion->>Chunker: split(content)
    Chunker-->>Ingestion: chunks
    Ingestion->>Index: index_document(...)
    Index-->>Ingestion: document_id, status, chunk_count
    Ingestion-->>Client: indexed
```

## Fluxo De Busca

```mermaid
sequenceDiagram
    participant Query
    participant Ingestion
    participant Index

    Query->>Ingestion: POST /search {project_id, query, top_k}
    Ingestion->>Index: search(project_id, query, top_k)
    Index-->>Ingestion: ranked chunks
    Ingestion-->>Query: chunks com location
```

## Estrutura

```text
app/
  config.py
  dependencies.py
  main.py
  domain/models.py              # IndexedDocument e IndexedChunk
  routers/ingestion.py          # HTTP
  schemas/ingestion.py          # contratos
  repositories/document_index.py # boundary do indice
  services/chunker.py           # chunking
  services/embedder.py          # boundary de embeddings
  services/retriever.py         # boundary de recuperacao
  services/ingestion_service.py # regras de ingestao
  services/token_validator.py   # dev/internal token
```

## Contratos

### Criar Documento

```json
{
  "project_id": "proj-demo",
  "material_id": "mat-architecture",
  "file_name": "architecture.md",
  "content": "texto do documento"
}
```

### Buscar

```json
{
  "project_id": "proj-demo",
  "query": "pergunta",
  "top_k": 5
}
```

Resposta:

```json
{
  "chunks": [
    {
      "document_id": "doc-1",
      "project_id": "proj-demo",
      "material_id": "mat-architecture",
      "file_name": "architecture.md",
      "location": "architecture.md#chunk-0",
      "chunk_index": 0,
      "chunk_text": "...",
      "score": 0.95
    }
  ]
}
```

## Azure Ownership

```mermaid
flowchart TB
    RG[Resource Group compartilhado] --> CA[Container App]
    RG --> SA[Storage Account]
    SA --> BC[Blob Container documents]
    RG --> AIS[Azure AI Search Free]
    RG --> APIM[API Management route /api/v1/ingestion]
```

## Execucao Local

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8003
```

## Qualidade

```bash
ruff check app tests
mypy app
python -m pytest
```

## Variaveis De Ambiente

| Variavel | Descricao |
| --- | --- |
| `BEARER_TOKEN` | Token dev para chamadas externas |
| `INTERNAL_SERVICE_TOKEN` | Token usado por query-service |
| `IDENTITY_SERVICE_URL` | Validador real opcional |
| `DEFAULT_CHUNK_MAX_WORDS` | Tamanho padrao dos chunks |

## Terraform

Este repo cria Blob Storage, AI Search Free, Container App e rota APIM.

```bash
scripts/terraform-bootstrap.sh
RUN_TERRAFORM_PLAN=true scripts/terraform-bootstrap.sh
```
