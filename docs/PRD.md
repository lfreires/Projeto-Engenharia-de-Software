# PRD Técnico — Módulo de Consulta (Chat RAG)

> **Disciplina:** Engenharia de Software com Microsserviços — Mackenzie 2026/1
> **Versão:** 1.1 | Abril 2026 — _atualizado: LLM migrado para Groq (free tier)_
> **Metodologia:** TDD First · CI/CD GitHub Actions · IaC Terraform (Azure)

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Stack de IA — Groq Free Tier](#2-stack-de-ia--groq-free-tier)
3. [Arquitetura](#3-arquitetura)
4. [Contrato de API](#4-contrato-de-api)
5. [Estratégia de TDD](#5-estratégia-de-tdd)
6. [Pipeline CI/CD](#6-pipeline-cicd)
7. [Infraestrutura como Código (Terraform)](#7-infraestrutura-como-código-terraform)
8. [Dockerfile](#8-dockerfile)
9. [Critérios de Aceite e Definition of Done](#9-critérios-de-aceite-e-definition-of-done)
10. [Cronograma](#10-cronograma)
11. [Dependências e Riscos](#11-dependências-e-riscos)

---

## 1. Visão Geral

### 1.1 Contexto

O Módulo de Consulta é um dos microsserviços da **Plataforma de Documentação Inteligente de Projetos de Engenharia de Software**. Ele implementa um chat baseado em **Retrieval-Augmented Generation (RAG)**: o usuário faz perguntas em linguagem natural sobre os artefatos de um projeto (código, diagramas, relatórios, atas) e a IA consulta os materiais indexados para responder com texto contextualizado e citação de fontes.

**v1.1:** o LLM foi migrado de OpenAI GPT-4o-mini (pago) para **Groq GroqCloud free tier** (`llama-3.3-70b-versatile`), e os embeddings passaram a rodar localmente via `sentence-transformers` — stack 100% gratuita para fins acadêmicos.

### 1.2 Problema a Resolver

- Desenvolvedores e PMs gastam tempo procurando informações espalhadas em repositórios, PDFs e chats.
- A documentação raramente reflete o estado atual do código.
- Não existe interface unificada de consulta sobre todos os artefatos do projeto.

### 1.3 Solução Proposta

Um microsserviço Python (FastAPI) que expõe um endpoint de chat. Internamente aplica o pipeline RAG:

1. Gera embedding da query localmente com `sentence-transformers` (sem custo).
2. Recupera chunks relevantes no **Azure AI Search** (free tier, vector search).
3. Constrói um prompt contextualizado e chama o LLM via **Groq API** (free tier).
4. Retorna a resposta ao front-end com citação das fontes usadas.

### 1.4 Escopo

| IN SCOPE | OUT OF SCOPE |
|---|---|
| Chat de perguntas e respostas em linguagem natural | Ingestão / indexação de documentos (módulo separado) |
| Respostas baseadas nos materiais indexados do projeto | Geração de diagramas (módulo de Diagramas) |
| Histórico de conversa por sessão | Autenticação de usuários (módulo de Gerenciamento) |
| Filtragem de resposta por `project_id` | Fine-tuning ou treinamento de modelos |
| API REST consumível pelo gateway da turma | Interface web própria (consumida pelo front da turma) |

---

## 2. Stack de IA — Groq Free Tier

### 2.1 Por que Groq?

| Critério | OpenAI (v1.0) | **Groq Free Tier (v1.1)** |
|---|---|---|
| Custo | ~$2/mês | **$0** |
| Cartão de crédito | Obrigatório | **Não necessário** |
| LLM | GPT-4o-mini | **Llama 3.3 70B** |
| Latência (token/s) | ~50 t/s | **~300 t/s (LPU)** |
| Compatibilidade SDK | OpenAI SDK | **OpenAI SDK** (mesma interface) |
| Embeddings | `text-embedding-3-small` (pago) | **`sentence-transformers` local (grátis)** |

> Groq expõe uma API 100% compatível com o SDK da OpenAI. A migração se resume a **3 linhas de código**: mudar `base_url`, trocar a chave e selecionar o model ID.

### 2.2 Modelos Selecionados

#### LLM — Groq GroqCloud

| Model ID | Parâmetros | Contexto | RPM | TPM | RPD | Uso |
|---|---|---|---|---|---|---|
| `llama-3.3-70b-versatile` | 70B | 128K | 30 | 6.000 | 1.000 | **Padrão** — respostas de alta qualidade |
| `llama-3.1-8b-instant` | 8B | 128K | 30 | 6.000 | 14.400 | **Fallback** — rate limit do 70B atingido |

**Estratégia de fallback:** se o 70B retornar `429 Too Many Requests`, o serviço faz retry automático com o 8B-instant (14x mais RPD). O cliente não percebe a troca.

#### Embeddings — `sentence-transformers` (local)

| Modelo | Dimensões | Tamanho | Onde roda | Custo |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | ~80 MB | Container (CPU) | **$0** |

O modelo é carregado em memória no startup do container. Latência de embedding ≈ 5–15ms para queries típicas em CPU.

### 2.3 Configuração do Cliente Groq

```python
# app/services/llm_client.py
from openai import OpenAI  # mesmo SDK — zero mudança de interface
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)

PRIMARY_MODEL  = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

def chat_completion(messages: list[dict], model: str = PRIMARY_MODEL) -> tuple[str, str]:
    """Retorna (resposta, model_used)."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content, model
    except Exception as e:
        if "429" in str(e) and model == PRIMARY_MODEL:
            return chat_completion(messages, model=FALLBACK_MODEL)
        raise
```

### 2.4 Limites do Free Tier e Estratégias de Mitigação

| Limite | Valor (70B) | Mitigação |
|---|---|---|
| RPM | 30 req/min | Fila de requests por usuário; max 1 simultânea |
| TPM | 6.000 tokens/min | Limitar contexto RAG a 2.000 tokens + histórico a 5 turnos |
| RPD | 1.000 req/dia | Fallback automático para `llama-3.1-8b-instant` (14.400 RPD) |

> **Para fins acadêmicos:** 1.000 RPD é mais que suficiente para demos, testes e apresentações. O fallback para 8B garante continuidade mesmo em dias de uso intenso.

### 2.5 Obter a Chave da API

```bash
# 1. Criar conta em https://console.groq.com (sem cartão de crédito)
# 2. Menu → API Keys → Create API Key
# 3. Armazenar no Azure Key Vault:
az keyvault secret set \
  --vault-name <KEY_VAULT_NAME> \
  --name "groq-api-key" \
  --value "<GROQ_API_KEY>"
```

---

## 3. Arquitetura

### 3.1 Diagrama de Componentes

```
[ Client / API Gateway da Turma ]
         |  POST /api/v1/query/chat
         v
[ Azure Container App: query-service ]
    FastAPI  +  RAG Pipeline
    /health  /chat  /history
       |                        |
[ Azure AI Search ]      [ Groq API (free) ]
  Vector Index (free)      llama-3.3-70b-versatile
       |                   llama-3.1-8b-instant (fallback)
[ Azure Blob Storage ]
  Chunks + Metadados JSON

[ sentence-transformers ]  <- roda dentro do container
  all-MiniLM-L6-v2           (sem chamada externa)
```

### 3.2 Serviços e Custos (Azure for Students)

| Serviço | Tier / SKU | Custo Est. | Finalidade |
|---|---|---|---|
| Azure Container Apps | Consumption (free grant) | ~$0/mês | Rodar a imagem Docker |
| Azure Container Registry | Basic | ~$5/mês | Armazenar imagem Docker |
| Azure AI Search | **Free** (50 MB, 3 índices) | $0/mês | Índice vetorial de chunks |
| Azure Blob Storage | LRS Standard | < $1/mês | Chunks e metadados JSON |
| Azure Key Vault | Standard | ~$0/mês | Secret: GROQ_API_KEY |
| **Groq API** | **Free tier** | **$0/mês** | **LLM: Llama 3.3 70B** |
| **sentence-transformers** | **Local (container)** | **$0** | **Embeddings** |
| **Total** | | **~$5/mês** | |

### 3.3 Pipeline RAG — Passo a Passo

1. Usuário envia `{ project_id, session_id, message }` via `POST /api/v1/query/chat`.
2. **Embedding local:** `sentence-transformers` gera vetor 384d da query (sem API externa).
3. **Retrieval:** busca top-k=5 chunks no Azure AI Search filtrados por `project_id`.
4. **Context Assembly:** concatena chunks respeitando limite de 2.000 tokens.
5. **Prompt Construction:** injeta system prompt + histórico (últimos 5 turnos) + contexto + query.
6. **LLM Call:** `llama-3.3-70b-versatile` via Groq API (`temperature=0`).
7. **Fallback automático:** se `429`, retry com `llama-3.1-8b-instant`.
8. **Response:** retorna JSON com `answer`, `sources[]`, `session_id` e `model_used`.

---

## 4. Contrato de API

### 4.1 Endpoints

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/query/health` | Nenhuma | Health check (liveness probe) |
| `POST` | `/api/v1/query/chat` | Bearer token | Enviar pergunta e receber resposta RAG |
| `GET` | `/api/v1/query/history/{session_id}` | Bearer token | Recuperar histórico de conversa |
| `DELETE` | `/api/v1/query/history/{session_id}` | Bearer token | Limpar histórico de sessão |

### 4.2 POST `/api/v1/query/chat`

**Request Body:**

```json
{
  "project_id": "string   [required] — UUID do projeto",
  "session_id": "string   [required] — UUID da sessão de chat",
  "message":    "string   [required] — Pergunta do usuário (max 2000 chars)",
  "top_k":      "integer  [optional, default: 5] — Chunks a recuperar"
}
```

**Response 200:**

```json
{
  "session_id": "string",
  "answer":     "string",
  "model_used": "llama-3.3-70b-versatile",
  "sources": [
    {
      "document_id": "string",
      "file_name":   "string",
      "chunk_index": 0,
      "score":       0.92
    }
  ],
  "latency_ms": 980
}
```

> O campo `model_used` indica se a resposta veio do modelo primário (70B) ou do fallback (8B).

### 4.3 Códigos de Erro

| HTTP | Código | Descrição |
|---|---|---|
| 400 | `INVALID_REQUEST` | `project_id` ou `message` ausentes/inválidos |
| 401 | `UNAUTHORIZED` | Token inválido ou ausente |
| 404 | `PROJECT_NOT_FOUND` | Nenhum documento indexado para `project_id` |
| 422 | `VALIDATION_ERROR` | Payload malformado (FastAPI padrão) |
| 429 | `RATE_LIMIT_EXCEEDED` | Ambos os modelos Groq com rate limit atingido |
| 503 | `LLM_UNAVAILABLE` | Groq API indisponível (circuit breaker aberto) |

---

## 5. Estratégia de TDD

### 5.1 Filosofia

> **Red → Green → Refactor.** Nenhum código de produção é escrito sem um teste que o justifique.

### 5.2 Pirâmide de Testes

| Nível | Ferramenta | Cobertura Alvo | O que testa |
|---|---|---|---|
| Unit | `pytest` + `pytest-mock` | >= 80% | Funções puras: embedding, chunking, prompt builder, fallback logic |
| Integration | `pytest` + `httpx` (ASGI) | >= 60% | Endpoints FastAPI com mocks de AI Search e Groq |
| E2E / Smoke | `pytest` + `requests` (staging) | Críticos | Health check + chat completo em staging real |

### 5.3 Casos de Teste Obrigatórios

#### Unit — RAG Pipeline

- `test_build_prompt_includes_context` — dado chunks, o prompt gerado contém o contexto.
- `test_build_prompt_respects_token_limit` — contexto nunca excede 2.000 tokens.
- `test_format_sources_returns_list` — fontes formatadas corretamente do retorno do search.
- `test_query_expansion_returns_string` — expansão retorna string não vazia.
- `test_chat_history_max_turns` — histórico truncado após N=5 turnos.

#### Unit — Groq Client e Fallback

- `test_llm_client_uses_primary_model` — primeira chamada usa `llama-3.3-70b-versatile`.
- `test_llm_client_fallback_on_429` — primário retorna `429` → retry automático com `llama-3.1-8b-instant`.
- `test_llm_client_raises_on_503` — ambos os modelos falham → propaga exceção.
- `test_response_includes_model_used` — campo `model_used` reflete o modelo que respondeu.

#### Unit — Embeddings Locais

- `test_embedding_returns_correct_dimension` — vetor tem 384 dimensões.
- `test_embedding_is_deterministic` — mesma query gera mesmo vetor.

#### Unit — Schemas e Validação

- `test_chat_request_missing_project_id_raises` — `ValidationError` se `project_id` ausente.
- `test_chat_request_message_too_long_raises` — `ValidationError` se `message` > 2000 chars.
- `test_chat_response_has_required_fields` — resposta contém `answer`, `sources`, `session_id`, `model_used`.

#### Integration — Endpoints

- `test_health_returns_200` — GET /health retorna `{ "status": "ok" }`.
- `test_chat_with_valid_payload_returns_200` — POST /chat com payload válido e mocks retorna 200.
- `test_chat_unknown_project_returns_404` — `project_id` sem docs indexados retorna 404.
- `test_chat_missing_token_returns_401` — ausência de Bearer token retorna 401.
- `test_chat_groq_429_triggers_fallback` — mock de 429 no 70B → resposta bem-sucedida via 8B.
- `test_chat_both_models_fail_returns_503` — ambos os modelos falhando → 503.
- `test_get_history_returns_messages` — GET /history retorna lista de turnos anteriores.
- `test_delete_history_clears_session` — DELETE /history retorna 204 e sessão fica vazia.

### 5.4 Estrutura de Diretórios

```
query-service/
├── app/
│   ├── main.py                # FastAPI app factory
│   ├── routers/
│   │   └── query.py           # Endpoints: /health /chat /history
│   ├── services/
│   │   ├── rag_pipeline.py    # Orquestrador RAG
│   │   ├── retriever.py       # Azure AI Search client
│   │   ├── embedder.py        # sentence-transformers (local)
│   │   ├── llm_client.py      # Groq client + fallback + circuit breaker
│   │   └── prompt_builder.py  # Construção de prompts
│   ├── schemas/
│   │   └── chat.py            # Pydantic models
│   └── config.py              # Settings via pydantic-settings
├── tests/
│   ├── unit/
│   │   ├── test_prompt_builder.py
│   │   ├── test_rag_pipeline.py
│   │   ├── test_llm_client.py    # testa fallback Groq
│   │   ├── test_embedder.py      # testa embeddings locais
│   │   └── test_schemas.py
│   └── integration/
│       └── test_endpoints.py
├── terraform/
├── .github/workflows/
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

### 5.5 Configuração pytest (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts   = "--cov=app --cov-report=term-missing --cov-fail-under=80 -v"

[tool.coverage.run]
omit = ["app/main.py", "tests/*"]
```

### 5.6 `requirements.txt`

```
fastapi
uvicorn[standard]
pydantic-settings
openai                      # SDK compatível com Groq (mesma interface)
sentence-transformers        # embeddings locais — sem API externa
azure-search-documents
azure-identity
azure-keyvault-secrets
tenacity                     # retry / circuit breaker
```

### 5.7 `requirements-dev.txt`

```
pytest
pytest-mock
pytest-cov
pytest-asyncio
httpx
ruff
mypy
```

---

## 6. Pipeline CI/CD

### 6.1 Workflows

| Workflow | Trigger | Etapas |
|---|---|---|
| `ci.yml` | push / PR → qualquer branch | lint → test → coverage → build Docker |
| `cd-staging.yml` | merge → `main` | build → push ACR → deploy Container App staging |
| `cd-prod.yml` | release tag `v*.*.*` | smoke test staging → deploy Container App prod |

### 6.2 `ci.yml`

```yaml
name: CI
on:
  push:
    branches: ['**']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt -r requirements.txt

      - name: Lint (ruff)
        run: ruff check app/ tests/

      - name: Type check (mypy)
        run: mypy app/ --ignore-missing-imports

      - name: Run tests + coverage
        env:
          GROQ_API_KEY: 'test-key'            # mock — sem chamadas reais ao Groq
          AZURE_SEARCH_KEY: 'test-key'
          AZURE_SEARCH_ENDPOINT: 'https://mock.search.windows.net'
        run: pytest

      - name: Build Docker image (smoke)
        run: docker build -t query-service:ci .
```

### 6.3 `cd-staging.yml`

```yaml
name: CD Staging
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build & Push to ACR
        run: |
          az acr build \
            --registry ${{ secrets.ACR_NAME }} \
            --image query-service:${{ github.sha }} .

      - name: Deploy to Container App (staging)
        run: |
          az containerapp update \
            --name query-service-staging \
            --resource-group ${{ secrets.RG_NAME }} \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/query-service:${{ github.sha }}

      - name: Smoke test staging
        run: |
          URL=$(az containerapp show \
            --name query-service-staging \
            --resource-group ${{ secrets.RG_NAME }} \
            --query 'properties.configuration.ingress.fqdn' -o tsv)
          curl -f https://$URL/api/v1/query/health
```

### 6.4 `cd-prod.yml`

```yaml
name: CD Production
on:
  push:
    tags: ['v*.*.*']

jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Container App (prod)
        run: |
          az containerapp update \
            --name query-service-prod \
            --resource-group ${{ secrets.RG_NAME }} \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/query-service:${{ github.sha }}
```

### 6.5 Secrets Necessários no GitHub

| Secret | Valor |
|---|---|
| `AZURE_CREDENTIALS` | JSON do Service Principal (`az ad sp create-for-rbac`) |
| `ACR_NAME` | Nome do Azure Container Registry |
| `RG_NAME` | Nome do Resource Group |
| `GROQ_API_KEY` | Chave do Groq (obtida em console.groq.com, sem cartão) |

---

## 7. Infraestrutura como Código (Terraform)

### 7.1 Estrutura

```
terraform/
├── main.tf           # Recursos principais
├── variables.tf      # Variáveis de entrada
├── outputs.tf        # Outputs (URLs, nomes)
└── terraform.tfvars  # Valores locais (no .gitignore)
```

### 7.2 `variables.tf`

```hcl
variable "resource_group_name" {
  description = "Nome do Resource Group"
  type        = string
  default     = "rg-query-service-dev"
}

variable "location" {
  description = "Região Azure"
  type        = string
  default     = "eastus"
}

variable "project_prefix" {
  description = "Prefixo único para nomes de recursos"
  type        = string
  default     = "mack"
}

variable "groq_api_key" {
  description = "Groq API Key (free tier — console.groq.com)"
  type        = string
  sensitive   = true
}
```

### 7.3 `main.tf`

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
  backend "azurerm" {}  # state remoto no Blob Storage
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

# ---- Resource Group ----
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# ---- Container Registry ----
resource "azurerm_container_registry" "acr" {
  name                = "${var.project_prefix}querysvcacr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

# ---- Storage Account ----
resource "azurerm_storage_account" "main" {
  name                     = "${var.project_prefix}querystorage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# ---- Azure AI Search (Free) ----
resource "azurerm_search_service" "main" {
  name                = "${var.project_prefix}-query-search"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "free"
}

# ---- Key Vault ----
resource "azurerm_key_vault" "main" {
  name                = "${var.project_prefix}-query-kv"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

# Groq API Key (substituiu OpenAI na v1.1)
resource "azurerm_key_vault_secret" "groq_key" {
  name         = "groq-api-key"
  value        = var.groq_api_key
  key_vault_id = azurerm_key_vault.main.id
}

# ---- Container Apps Environment ----
resource "azurerm_container_app_environment" "main" {
  name                = "${var.project_prefix}-query-env"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

# ---- Container App ----
resource "azurerm_container_app" "query_service" {
  name                         = "query-service"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  template {
    min_replicas = 0
    max_replicas = 3

    container {
      name   = "query-service"
      image  = "${azurerm_container_registry.acr.login_server}/query-service:latest"
      # sentence-transformers precisa de memória suficiente para carregar o modelo (~80MB)
      cpu    = 0.5
      memory = "1.5Gi"

      env {
        name        = "GROQ_API_KEY"
        secret_name = "groq-api-key"
      }
      env {
        name  = "AZURE_SEARCH_ENDPOINT"
        value = "https://${azurerm_search_service.main.name}.search.windows.net"
      }
      env {
        name  = "PRIMARY_LLM_MODEL"
        value = "llama-3.3-70b-versatile"
      }
      env {
        name  = "FALLBACK_LLM_MODEL"
        value = "llama-3.1-8b-instant"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }
}
```

### 7.4 `outputs.tf`

```hcl
output "container_app_url" {
  value = "https://${azurerm_container_app.query_service.ingress[0].fqdn}"
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "search_endpoint" {
  value = "https://${azurerm_search_service.main.name}.search.windows.net"
}
```

### 7.5 Bootstrap (executar uma vez)

```bash
# 1. Login
az login
az account set --subscription <SUBSCRIPTION_ID>

# 2. Criar storage para Terraform state
az group create -n rg-tfstate -l eastus
az storage account create -n mackterraformstate -g rg-tfstate -l eastus --sku Standard_LRS
az storage container create -n tfstate --account-name mackterraformstate

# 3. Inicializar e aplicar
cd terraform/
terraform init \
  -backend-config="resource_group_name=rg-tfstate" \
  -backend-config="storage_account_name=mackterraformstate" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=query-service.tfstate"

terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars -auto-approve

# 4. Destruir quando não estiver usando (economizar crédito Azure)
terraform destroy -var-file=terraform.tfvars -auto-approve
```

---

## 8. Dockerfile

```dockerfile
# ---- Build stage ----
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ ./app/
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Pré-baixar o modelo de embedding durante o build da imagem.
# Evita cold start lento no primeiro request em produção.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> O `RUN python -c "..."` faz download do modelo (~80 MB) durante o `docker build`, eliminando o cold start no primeiro request. Imagem final: ~500 MB.

---

## 9. Critérios de Aceite e Definition of Done

### 9.1 Definition of Done (DoD) por User Story

- [ ] Código escrito **após** o teste (TDD — Red → Green → Refactor).
- [ ] Cobertura de testes >= 80% no módulo alterado.
- [ ] Lint (`ruff`) e type check (`mypy`) passando sem erros.
- [ ] PR aprovado por ao menos 1 membro do grupo.
- [ ] CI pipeline verde no GitHub Actions.
- [ ] Deploy em staging com smoke test passando.
- [ ] Endpoint documentado no Swagger (`/docs` — FastAPI automático).

### 9.2 Critérios de Aceite por Funcionalidade

| Funcionalidade | Critério de Aceite |
|---|---|
| Chat RAG básico | Dado um `project_id` com docs indexados, retorna resposta com ao menos 1 `source` em < 10s. |
| Fallback de modelo | Quando o 70B retorna 429, o serviço responde via 8B sem erro para o cliente. Campo `model_used` reflete o modelo real. |
| Histórico de sessão | Últimos 5 turnos influenciam a resposta atual (follow-up questions funcionam). |
| Filtro por projeto | Respostas do projeto A não contêm chunks do projeto B. |
| Embeddings locais | Embedding gerado sem nenhuma chamada de rede externa. |
| Health check | `GET /health` retorna 200 com `{ "status": "ok" }` em < 200ms. |
| Integração com turma | Endpoint acessível via URL pública do Container App; aceita Bearer token do módulo de autenticação. |

### 9.3 Mapeamento para Rubrica Mackenzie

| Critério | Peso | Como atender |
|---|---|---|
| Funcionamento | 0/1 | Serviço sobe e responde ao `/health`. |
| Integração | 0.5/1 | Integração validada com Ingestão ou Gerenciamento. |
| Funcionalidade | 5 | Todos os endpoints implementados e critérios de aceite atendidos. |
| Qualidade | 2 | Cobertura >= 80%, lint limpo, código organizado e documentado. |
| Robustez | 2 | Fallback de modelo, circuit breaker, graceful shutdown, liveness probe, escala 0→N. |
| Conceitos | 1 | TDD evidenciado nos commits, IaC Terraform, CI/CD completo. |

---

## 10. Cronograma

| Entrega | Data | Atividades | Artefatos |
|---|---|---|---|
| P5 | 12/04 | MVP: `/health` + `/chat` com RAG básico (mocks de AI Search e Groq). TDD unit tests. | Código + testes + README |
| AP1 | 13–17/04 | Demo do endpoint `/chat` funcionando localmente via Docker Compose. | Apresentação parcial |
| P6 | 19/04 | Primeiro commit com CI verde. Terraform state bootstrap. Contrato de embedding alinhado com grupo de Ingestão. | Repositório + GitHub Actions |
| P7 | 26/04 | Revisão do backlog: priorizar fallback, circuit breaker e integração. | Backlog atualizado |
| P8 | 10/05 | Terraform aplicado: todos os recursos Azure provisionados. | Diagrama de arquitetura |
| P9 | 17/05 | Primeiro deploy real no Container App. CD pipeline funcionando. | URL pública em staging |
| P10 | 24/05 | Código completo. E2E smoke tests. Integração com demais grupos validada. | Commit final + release tag |
| AP2 | 25–29/05 | Apresentação final + relatório técnico do módulo. | Slides + relatório |

---

## 11. Dependências e Riscos

### 11.1 Dependências Externas

- **Módulo de Ingestão (outro grupo):** deve usar o **mesmo modelo de embedding** (`all-MiniLM-L6-v2`, 384 dimensões) ao indexar chunks. Schema acordado:
  ```json
  { "project_id": "uuid", "chunk_text": "string", "embedding": [float x 384], "document_id": "uuid" }
  ```
- **Módulo de Gerenciamento (outro grupo):** fornece o Bearer token e o contrato de autenticação JWT.
- **Groq API (free tier):** dependência externa gratuita; mitigada com fallback de modelo e circuit breaker.

### 11.2 Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Groq RPD (1.000/dia no 70B) atingido | Média | Fallback automático para `llama-3.1-8b-instant` (14.400 RPD). |
| Groq indisponível (outage) | Baixa | Circuit breaker com `tenacity`; resposta de fallback informativa ao usuário. |
| AI Search free tier (50 MB) esgotado | Média | Limitar chunks a 512 tokens; comprimir metadados. |
| Schema de embeddings divergente entre grupos | **Alta** | Alinhar modelo (`all-MiniLM-L6-v2`, 384d) com grupo de Ingestão no P6. |
| Cold start lento do sentence-transformers | Baixa | Modelo pré-baixado no `docker build`; staging mantém réplica aquecida. |
| Crédito Azure for Students esgotado | Baixa | `terraform destroy` quando não usar; Container App escala a zero automaticamente. |

---

*PRD Técnico — Módulo de Consulta | Mackenzie 2026/1 | v1.1 — Groq free tier*
