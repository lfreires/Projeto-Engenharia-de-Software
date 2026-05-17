# docai-identity-service

Servico FastAPI responsavel por identidade simples no MVP: tokens dev/API key,
usuarios demo, service clients internos e memberships por projeto. Ele nao faz
login, senha, refresh token ou emissao JWT.

## Arquitetura

```mermaid
flowchart LR
    Client[Servicos ou Frontend] -->|POST /tokens/validate| API[identity router]
    API --> SVC[IdentityService]
    SVC --> REPO[IdentityRepository]
    REPO -->|local| MEM[InMemoryIdentityRepository]
    REPO -->|prod futuro| SQL[Azure SQL Database]
```

## Fluxo De Validacao

```mermaid
sequenceDiagram
    participant Service
    participant Identity
    participant Repository

    Service->>Identity: POST /tokens/validate
    Identity->>Repository: get_token(token)
    Repository-->>Identity: subject + permissions
    Identity->>Repository: list_memberships(project_id)
    Identity-->>Service: active, subject_id, permissions
```

## Estrutura

```text
app/
  config.py
  dependencies.py
  domain.py                         # fachada compatibilidade
  main.py
  routers/identity.py
  schemas/identity.py
  repositories/identity_repository.py
  services/identity_service.py
```

## Endpoints

- `GET /api/v1/identity/health`
- `POST /api/v1/identity/tokens/validate`
- `GET /api/v1/identity/users`
- `GET /api/v1/identity/memberships`

## Modelo De Dados

```mermaid
erDiagram
    users ||--o{ project_memberships : has
    users ||--o{ api_tokens : owns
    service_clients ||--o{ api_tokens : owns
    users {
      string id
      string email
      string display_name
    }
    api_tokens {
      string token_hash
      string subject_id
      string subject_type
      boolean active
    }
    service_clients {
      string id
      string name
    }
    project_memberships {
      string project_id
      string user_id
      string role
    }
```

## Azure Ownership

```mermaid
flowchart TB
    Identity[identity-service terraform] --> RG[Resource Group]
    Identity --> ACR[Azure Container Registry Basic]
    Identity --> LAW[Log Analytics]
    Identity --> CAE[Container Apps Environment]
    Identity --> APIM[API Management Consumption]
    Identity --> KV[Key Vault]
    Identity --> SQL[Azure SQL Serverless]
```

## Execucao Local

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8001
```

## Qualidade

```bash
ruff check app tests
mypy app
python -m pytest
```

## Terraform

```bash
export TF_VAR_sql_admin_password="..."
scripts/terraform-bootstrap.sh
RUN_TERRAFORM_PLAN=true scripts/terraform-bootstrap.sh
```

Remote state opcional: `TF_BACKEND_RESOURCE_GROUP`,
`TF_BACKEND_STORAGE_ACCOUNT`, `TF_BACKEND_CONTAINER`, `TF_BACKEND_KEY`.
