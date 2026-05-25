# CLAUDE.md

## Project Overview

DocAI is a RAG demonstration application deployed as a monorepo on Render.
The React/Vite SPA is a Render Static Site and the FastAPI API is a separate
Render Docker web service. Persistent state and vector search use a Supabase
PostgreSQL project with `pgvector`.

## Runtime Architecture

| Component | Location | Responsibility |
| --- | --- | --- |
| Frontend | `frontend/` | Render Static Site for chat and materials UI |
| Backend | `backend/app/` | Consolidated FastAPI API Docker service |
| Database | Supabase Postgres | Domain/chat records and LangChain PGVector collection |
| Embeddings | Gemini API | `gemini-embedding-2`, 768-dimensional vectors |
| Answer model | Groq API | LangChain RAG response generation |
| Deploy | `render.yaml` | One Render web service plus one Static Site |

Public API prefixes remain compatible with the former service split:

- `/api/v1/identity`
- `/api/v1/projects`
- `/api/v1/ingestion`
- `/api/v1/query`
- `/health` for Render health checks

## Persistence

`backend/migrations/` owns the domain schema. At application startup in
production, the backend applies unapplied migrations and performs an
idempotent demo seed. The seed creates `proj-demo`, identity and token
`dev-token`; it does not create material or indexed content.

Persistent domains:

- Identity: `users`, `api_tokens`, `project_memberships`
- Catalog: `projects`, `materials`, `material_versions`
- RAG catalog: `documents` with extracted content and indexing status
- RAG vectors: LangChain Postgres collection
  `docai_documents_gemini_embedding_2_768_v1`
- Conversation: `chat_sessions`, `messages`, `feedback`

## Configuration

Render-required secrets:

- `DATABASE_URL`: Supabase Postgres/Supavisor connection string
- `GROQ_API_KEY`: answer generation
- `GEMINI_API_KEY`: document and query embeddings

Blueprint defaults:

- `APP_ENV=production`
- `BEARER_TOKEN=dev-token`
- `INTERNAL_SERVICE_TOKEN=internal-query-token`
- `PRIMARY_LLM_MODEL=llama-3.3-70b-versatile`
- `FALLBACK_LLM_MODEL=llama-3.1-8b-instant`
- `EMBEDDING_MODEL=gemini-embedding-2`
- `EMBEDDING_DIMENSIONS=768`
- `VECTOR_COLLECTION_NAME=docai_documents_gemini_embedding_2_768_v1`

The browser token is demonstrative and is not production authentication.
Use a Supabase Session Pooler or Transaction Pooler `DATABASE_URL`: Render
cannot reach Supabase's direct IPv6-only `db.<ref>.supabase.co` host.

The frontend build receives `VITE_API_BASE_URL=https://docai-v8qm.onrender.com`
from the Blueprint, matching the currently provisioned backend URL. The API
permits Render static-site origins through CORS for this demonstration
deployment.

## Document Ingestion

The frontend Materials panel uploads `PDF`, `DOCX`, `TXT` and `MD` documents
up to 10 MB through `POST /api/v1/ingestion/uploads`. Each upload creates one
material, extracts readable text through LangChain loaders, splits it with
LangChain splitters and indexes it through `langchain-postgres` PGVector. The
application persists extracted text for the reader, not the original binary.

Markdown headings and PDF page metadata are retained in retrieval metadata.
Chat citations expose the document name rather than internal chunk IDs.

## Development Commands

Backend:

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
python -m ruff check app tests
uvicorn app.main:app --reload --port 8000
```

Without `APP_ENV=production` and `DATABASE_URL`, the backend uses an in-memory
development store and deterministic local embeddings.

Frontend:

```bash
cd frontend
npm ci
npm run dev
npm run build
```

The Vite development proxy routes `/api` to `http://localhost:8000` when
`VITE_API_BASE_URL` is empty. In production it calls the backend web service.

Deployment instructions are in `docs/DEPLOY.md`.
