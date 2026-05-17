# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DocAI** — a microservices-based RAG (Retrieval-Augmented Generation) document AI system. Users upload documents to projects and ask questions; the system retrieves relevant chunks and generates answers via Groq/LangChain.

## Architecture

Five independently deployable services:

| Service | Port | Responsibility |
|---|---|---|
| `frontend` | 5173 | React/Vite SPA — project management UI, chat interface |
| `identity-service` | 8001 | Token validation (dev: static "dev-token") |
| `project-service` | 8002 | Project/material catalog (in-memory for dev) |
| `ingestion-service` | 8003 | Document ingestion → Azure Blob + Azure AI Search |
| `query-service` | 8004 | RAG orchestration via LangChain + Groq |

**Cloud target:** Azure (Container Apps, API Management, Blob Storage, AI Search, Key Vault, Cosmos DB).

### Request Flow

```
Frontend → identity-service (auth) → project-service (catalog)
                                   → ingestion-service (upload/search)
                                   → query-service (RAG chat)
```

### Data stores

- Dev: in-memory (users, tokens, projects, sessions, feedback)
- Prod target: PostgreSQL Flexible Server, Azure Cosmos DB

## Development Commands

### Frontend

```bash
cd frontend
npm ci
npm run dev          # http://localhost:5173
npm run build        # production build
```

### Backend services (same pattern for each)

```bash
cd <service-dir>
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port <port>
```

### Quality checks (backend)

```bash
ruff check app tests   # lint
mypy app               # type check
python -m pytest       # tests (80% coverage minimum)
```

### Real Groq E2E tests (query-service only)

```bash
RUN_REAL_GROQ_E2E=true python -m pytest
```

## Environment Variables

**Frontend** (`.env` or inline):
- `VITE_API_BASE_URL` — backend gateway URL
- `VITE_PROJECT_ID` — default project ID
- `VITE_BEARER_TOKEN` — use `dev-token` locally

**Query service:**
- `GROQ_API_KEY` — required
- `INGESTION_SERVICE_URL` — URL of ingestion-service

**All backend services** (optional for dev):
- `IDENTITY_SERVICE_URL`
- `BEARER_TOKEN` — defaults to `dev-token` in dev mode

## Infrastructure & Deploy

Full bootstrap guide: `docs/DEPLOY.md`

**Bootstrap (one-time, run locally by the person with Azure for Students):**

```bash
# Edit GITHUB_REPOS array in the script first
export TF_VAR_sql_admin_password="..."
export TF_VAR_postgres_admin_password="..."
bash scripts/bootstrap-all.sh
```

The script provisions all Azure resources in dependency order and prints every GitHub Secret/Variable that each team member needs to configure in their repo.

**Per-service Terraform (individual apply if needed):**

```bash
scripts/terraform-bootstrap.sh                  # validate/plan
RUN_TERRAFORM_PLAN=true scripts/terraform-bootstrap.sh
```

## CI/CD

Each service has its own GitHub Actions workflows:
- `ci.yml` — lint → type check → test → Docker build (triggers on PR/push to main)
- `cd.yml` — OIDC login → ACR push → Container App update → `/health` smoke test

**Authentication:** uses OIDC with a User-assigned Managed Identity (no service principal, no App Registration required). GitHub secrets needed per backend repo: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. Frontend uses `AZURE_STATIC_WEB_APPS_API_TOKEN`.

## Key Patterns

- **Auth**: Bearer token passed in `Authorization` header; identity-service validates it. Dev token `dev-token` bypasses real auth.
- **Inter-service calls**: HTTPX async client; each service independently validates the bearer token.
- **Ingestion pipeline**: Upload → Azure Blob Storage → chunk & embed → Azure AI Search index.
- **RAG query**: Retrieve top-k chunks from Azure AI Search → assemble prompt → Groq LLM via LangChain → stream response.
- **Config**: Pydantic `BaseSettings` in each service (`app/config.py`); env vars override defaults.
