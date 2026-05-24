# CLAUDE.md

## Project Overview

DocAI is a RAG demonstration application deployed as a monorepo on Render.
The React/Vite SPA and the FastAPI API are delivered from one Docker web
service. Persistent state and vector search use a Supabase PostgreSQL project
with `pgvector`.

## Runtime Architecture

| Component | Location | Responsibility |
| --- | --- | --- |
| Frontend | `frontend/` | Chat and materials UI, compiled into the API image |
| Backend | `backend/app/` | Consolidated FastAPI API and SPA hosting |
| Database | Supabase Postgres | Domain records, chat records and vector chunks |
| Embeddings | Gemini API | `gemini-embedding-001`, 768-dimensional vectors |
| Answer model | Groq API | RAG response generation |
| Deploy | `render.yaml` | One Render free Docker web service |

Public API prefixes remain compatible with the former service split:

- `/api/v1/identity`
- `/api/v1/projects`
- `/api/v1/ingestion`
- `/api/v1/query`
- `/health` for Render health checks

## Persistence

`backend/migrations/001_initial.sql` owns the database schema. At application
startup in production, the backend applies unapplied migrations and performs
an idempotent demo seed. The seed creates `proj-demo`, token `dev-token`, one
material and an indexed architecture document.

Persistent domains:

- Identity: `users`, `api_tokens`, `project_memberships`
- Catalog: `projects`, `materials`, `material_versions`
- RAG: `documents`, `document_chunks` with `extensions.vector(768)`
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
- `EMBEDDING_MODEL=gemini-embedding-001`
- `EMBEDDING_DIMENSIONS=768`

The browser token is demonstrative and is not production authentication.

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

The Vite development proxy routes `/api` to `http://localhost:8000`. In
production, both UI and API use the same Render origin.

Deployment instructions are in `docs/DEPLOY.md`.
