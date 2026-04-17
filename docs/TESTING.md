# Manual de Testes Locais

Este documento cobre todos os cenários de teste do DocAI: testes unitários do backend, testes de integração, execução via Docker Compose e validação manual das chamadas de API.

---

## Pré-requisitos

| Ferramenta | Versão mínima | Instalação |
|---|---|---|
| Python | 3.12 | [python.org](https://python.org) |
| Node.js | 18 LTS | [nodejs.org](https://nodejs.org) |
| Docker + Compose | Docker 24 / Compose v2 | [docker.com](https://docker.com) |
| curl | qualquer | pré-instalado no Linux/macOS; `winget install curl` no Windows |

---

## 1. Testes do Backend (pytest)

### 1.1 Setup do ambiente

```bash
cd query-service

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 1.2 Executar todos os testes com cobertura

```bash
pytest
```

Saída esperada:

```
tests/unit/test_schemas.py          ............       PASSED
tests/unit/test_prompt_builder.py   .......            PASSED
tests/unit/test_embedder.py         ...                PASSED
tests/unit/test_llm_client.py       .....              PASSED
tests/unit/test_rag_pipeline.py     ...                PASSED
tests/integration/test_endpoints.py .................. PASSED

---------- coverage: app ----------
TOTAL                               82%

✓ 80% coverage threshold met
```

### 1.3 Rodar apenas testes unitários

```bash
pytest tests/unit/ -v
```

### 1.4 Rodar apenas testes de integração

```bash
pytest tests/integration/ -v
```

### 1.5 Ver relatório de cobertura detalhado (HTML)

```bash
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### 1.6 Lint e typecheck

```bash
ruff check app/ tests/       # linter (PEP8 + imports)
mypy app/ --ignore-missing-imports  # verificação de tipos
```

---

## 2. O que cada suite de testes valida

### Testes Unitários

| Arquivo | O que testa |
|---|---|
| `test_schemas.py` | Validação Pydantic: campos obrigatórios, max_length, tipos |
| `test_prompt_builder.py` | Construção de prompt com contexto, limite de tokens, histórico max 5 turnos, formatação de fontes |
| `test_embedder.py` | Vetor 384d, determinismo, tipo float[] (sentence-transformers mockado) |
| `test_llm_client.py` | Uso do modelo primário, fallback automático no 429, propagação de 503 |
| `test_rag_pipeline.py` | Orquestrador completo com mocks: resposta correta, 404 sem chunks, histórico enviado ao LLM |

### Testes de Integração (ASGI)

| Caso de teste | Cenário |
|---|---|
| `test_health_returns_200` | GET /health sem auth → 200 `{"status":"ok"}` |
| `test_chat_with_valid_payload_returns_200` | POST /chat com payload correto → 200 com answer |
| `test_chat_missing_token_returns_401` | POST /chat sem Bearer token → 401 |
| `test_chat_unknown_project_returns_404` | project_id sem docs indexados → 404 |
| `test_chat_groq_429_triggers_fallback` | Mock de 429 no 70B → resposta com model_used = 8B |
| `test_chat_both_models_fail_returns_503` | Ambos os modelos falham → 503 |
| `test_get_history_returns_messages` | GET /history após um chat → lista de turnos |
| `test_delete_history_clears_session` | DELETE /history → 204, GET /history → lista vazia |

---

## 3. Servidor Backend Local (sem Docker)

```bash
cd query-service
cp .env.example .env

# Preencha no .env:
#   GROQ_API_KEY=gsk_...
#   AZURE_SEARCH_ENDPOINT=https://seu-servico.search.windows.net
#   AZURE_SEARCH_KEY=...
#   AZURE_SEARCH_INDEX=documents

uvicorn app.main:app --reload --port 8000
```

Acesse `http://localhost:8000/docs` para a interface Swagger interativa.

> **Nota:** na primeira inicialização o modelo `all-MiniLM-L6-v2` (~80 MB) é carregado em memória. Isso leva cerca de 10–20 segundos em CPU.

---

## 4. Frontend Local (sem Docker)

```bash
# Na raiz do repositório
cp .env.local.example .env.local
# Edite VITE_PROJECT_ID e VITE_BEARER_TOKEN se necessário

npm install
npm run dev
```

Acesse `http://localhost:5173`. O Vite proxia automaticamente `/api/*` → `http://localhost:8000`.

---

## 5. MVP Completo com Docker Compose

### 5.1 Primeira execução

```bash
# Configure as variáveis do backend
cp query-service/.env.example query-service/.env
# Edite query-service/.env com GROQ_API_KEY e Azure Search

# Build e start (primeira vez: ~3–5 min)
docker compose up --build
```

### 5.2 Execuções subsequentes

```bash
docker compose up           # sem rebuild
docker compose up --build   # com rebuild das imagens
```

### 5.3 Logs

```bash
docker compose logs backend    # logs do FastAPI
docker compose logs frontend   # logs do nginx
docker compose logs -f         # follow ambos
```

### 5.4 Parar e limpar

```bash
docker compose down            # para containers (mantém volumes)
docker compose down -v         # para + remove volumes
docker compose down --rmi all  # para + remove imagens
```

---

## 6. Health Check Automatizado

O script `scripts/health-check.sh` testa o sistema de ponta a ponta:

```bash
# Ambiente local (Docker Compose rodando)
bash scripts/health-check.sh

# Ambiente remoto (produção)
BACKEND_URL=https://mack-query-service.azurecontainerapps.io \
FRONTEND_URL=https://mack-query-frontend.azurecontainerapps.io \
BEARER_TOKEN=seu-token-de-prod \
bash scripts/health-check.sh
```

O script verifica:
1. `GET /api/v1/query/health` → 200 com `{"status":"ok"}`
2. `POST /chat` sem token → 401 (auth funcionando)
3. `GET /history` autenticado → 200 (endpoints de sessão)
4. `GET /` no frontend → 200 (nginx servindo SPA)
5. `POST /chat` completo com query RAG real (requer Azure Search com docs indexados)

---

## 7. Testes Manuais via curl

### Health check

```bash
curl http://localhost:8000/api/v1/query/health
# → {"status":"ok"}
```

### Chat sem token (deve retornar 401)

```bash
curl -X POST http://localhost:8000/api/v1/query/chat \
  -H "Content-Type: application/json" \
  -d '{"project_id":"p1","session_id":"s1","message":"oi"}'
# → 401
```

### Chat com token e projeto inexistente (deve retornar 404)

```bash
curl -X POST http://localhost:8000/api/v1/query/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{"project_id":"projeto-inexistente","session_id":"s1","message":"oi"}'
# → 404 PROJECT_NOT_FOUND
```

### Chat completo (requer Azure Search com docs indexados)

```bash
curl -X POST http://localhost:8000/api/v1/query/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "project_id": "ecommerce-api",
    "session_id": "test-session-001",
    "message": "Qual é a arquitetura do sistema?",
    "top_k": 5
  }' | python3 -m json.tool
```

### Feedback

```bash
curl -X POST http://localhost:8000/api/v1/query/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "session_id": "test-session-001",
    "message_id": "ai-1713312000000",
    "rating": "positive",
    "comment": "Resposta clara e precisa"
  }'
# → {"accepted":true,"message_id":"ai-1713312000000"}
```

### Histórico de sessão

```bash
curl -H "Authorization: Bearer dev-token" \
  http://localhost:8000/api/v1/query/history/test-session-001 | python3 -m json.tool
```

### Limpar sessão

```bash
curl -X DELETE -H "Authorization: Bearer dev-token" \
  http://localhost:8000/api/v1/query/history/test-session-001
# → 204 No Content
```

---

## 8. Problemas Comuns

| Problema | Causa | Solução |
|---|---|---|
| `OSError: [Errno 99] Cannot assign requested address` | Porta em uso | `docker compose down` ou mudar porta no compose |
| Backend demora 30s para responder no primeiro request | sentence-transformers carregando o modelo | Normal. O compose tem `start_period: 30s` no healthcheck |
| `404 PROJECT_NOT_FOUND` no chat | Nenhum documento indexado para o `project_id` | Verificar `VITE_PROJECT_ID` e se o módulo de Ingestão indexou documentos com o mesmo ID |
| `503 LLM_UNAVAILABLE` | GROQ_API_KEY inválida ou Groq fora do ar | Verificar chave em console.groq.com; o fallback para llama-3.1-8b é automático no 429 |
| Frontend mostra erro de CORS | Backend não está rodando | `docker compose up` ou `uvicorn app.main:app` |
| `pytest: collected 0 items` | Ambiente virtual não ativo | `source .venv/bin/activate` |
| `ImportError: sentence_transformers` | Dependência não instalada | `pip install -r requirements.txt` |
