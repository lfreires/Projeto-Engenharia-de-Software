# Guia de Deploy — DocAI

Este documento descreve o processo completo para fazer o deploy do DocAI em 5 repositórios separados no Azure for Students, sem necessidade de App Registration ou acesso ao Entra ID.

---

## Visão Geral da Arquitetura de Deploy

```
Azure for Students (1 conta)
└── rg-docai-student
    ├── Recursos compartilhados (criados pelo identity-service)
    │   ├── Container Registry (ACR)
    │   ├── Container App Environment
    │   ├── API Management (gateway)
    │   ├── Key Vault
    │   └── github-actions-mi (User-assigned Managed Identity)
    │       └── federated credentials (1 por repo GitHub)
    ├── identity-service  → Azure SQL Database
    ├── project-service   → PostgreSQL Flexible Server
    ├── ingestion-service → Azure AI Search + Blob Storage
    ├── query-service     → Cosmos DB
    └── frontend          → Static Web App
```

**Autenticação CI/CD:** cada repositório usa OIDC (sem secrets de longa duração) via a Managed Identity criada no bootstrap. Nenhum Service Principal ou App Registration é necessário.

---

## Pré-requisitos

Quem executa o bootstrap precisa ter:

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) instalado
- [Terraform >= 1.6.0](https://developer.hashicorp.com/terraform/install) instalado
- Conta Azure for Students com crédito disponível
- Os 5 repositórios GitHub já criados (podem estar vazios)

---

## Passo a Passo: Bootstrap (feito uma única vez pela pessoa com Azure)

### 1. Editar os nomes dos repositórios

Abra `scripts/bootstrap-all.sh` e edite o array `GITHUB_REPOS` com os repos reais do grupo:

```bash
GITHUB_REPOS=(
  "usuario1/docai-identity-service"
  "usuario2/docai-project-service"
  "usuario3/docai-ingestion-service"
  "usuario4/docai-query-service"
  "usuario1/docai-frontend"          # frontend fica no repo de quem preferir
)
```

### 2. Fazer login no Azure

```bash
az login
az account show   # confirmar que está na subscription do Azure for Students
```

### 3. Definir as senhas dos bancos

```bash
export TF_VAR_sql_admin_password="SuaSenhaSQL123!"
export TF_VAR_postgres_admin_password="SuaSenhaPG123!"
```

> Regras: mínimo 8 caracteres, letras maiúsculas, minúsculas e números.

### 4. Executar o bootstrap

```bash
bash scripts/bootstrap-all.sh
```

O script leva entre 15 e 30 minutos (a maior parte é o APIM Consumption). Ao final, ele imprime no terminal **todos os GitHub Secrets e Variables** que cada pessoa precisa configurar.

> **Importante:** copie o output antes de fechar o terminal. O `SWA_TOKEN` do frontend só aparece aqui.

### 5. Reexecutar se necessário

O script é idempotente — pode ser executado novamente sem problemas. O Terraform apenas aplica as diferenças. Use as mesmas variáveis de ambiente.

---

## Passo a Passo: Configurar cada repositório GitHub (feito por cada pessoa)

Após receber os valores do bootstrap, cada pessoa configura o próprio repositório.

### Navegar até as configurações

`GitHub → seu repo → Settings → Environments → production`

Se o environment `production` não existir, crie-o antes.

### Backends (identity, project, ingestion, query)

Adicionar em **Secrets**:

| Secret | Valor |
|---|---|
| `AZURE_CLIENT_ID` | (recebido do bootstrap) |
| `AZURE_TENANT_ID` | (recebido do bootstrap) |
| `AZURE_SUBSCRIPTION_ID` | (recebido do bootstrap) |

Adicionar em **Variables**:

| Variable | Valor |
|---|---|
| `ACR_NAME` | (recebido do bootstrap) |
| `ACR_LOGIN_SERVER` | (recebido do bootstrap) |
| `CONTAINER_APP_NAME` | (específico do seu serviço — recebido do bootstrap) |
| `RESOURCE_GROUP` | `rg-docai-student` |
| `HEALTH_URL` | (URL do seu Container App + `/health`) |

### Frontend

Adicionar em **Secrets**:

| Secret | Valor |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | (recebido do bootstrap) |
| `VITE_BEARER_TOKEN` | `dev-token` |

Adicionar em **Variables**:

| Variable | Valor |
|---|---|
| `VITE_API_BASE_URL` | URL do API Management (recebido do bootstrap) |
| `VITE_PROJECT_ID` | `proj-demo` |

---

## Separação dos repositórios

Após o bootstrap, cada microserviço vive em um repositório independente. Para separar a partir deste monorepo:

```bash
# Exemplo para o project-service
git clone <url-do-repo-vazio> ../docai-project-service
cp -r project-service/* ../docai-project-service/
cp project-service/.github ../docai-project-service/ -r
cd ../docai-project-service
git add .
git commit -m "feat: initial project-service"
git push origin main
```

Cada push para `main` dispara o workflow de CD, que:
1. Autentica no Azure via OIDC (sem secrets de longa duração)
2. Faz build da imagem Docker
3. Faz push para o ACR compartilhado
4. Atualiza o Container App com a nova imagem
5. Executa smoke test em `/health`

---

## Variáveis de ambiente dos serviços (pós-deploy)

Algumas variáveis precisam ser configuradas diretamente no Container App após o deploy (via portal ou `az containerapp update --set-env-vars`):

| Serviço | Variável | Onde obter |
|---|---|---|
| query-service | `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| query-service | `INTERNAL_SERVICE_TOKEN` | Definir um token compartilhado entre serviços |
| ingestion-service | `AZURE_SEARCH_KEY` | Azure Portal → Search Service → Keys |
| ingestion-service | `AZURE_SEARCH_ENDPOINT` | Azure Portal → Search Service → Overview |
| todos os backends | `BEARER_TOKEN` | Mesmo valor que `VITE_BEARER_TOKEN` do frontend |

---

## Troubleshooting

### Workflow falha com "AADSTS70011: The provided request must include a 'scope' input parameter"

O federated credential não foi criado para este repositório. Verificar se o nome do repo no array `GITHUB_REPOS` do script de bootstrap está correto e reexecutar.

### Terraform falha com "The subscription is not registered to use namespace"

```bash
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Search
```

### Container App não atualiza após push

Verificar se `CONTAINER_APP_NAME` e `RESOURCE_GROUP` estão corretos no environment do GitHub.

### APIM demora muito para provisionar

O APIM Consumption pode levar até 40 minutos na primeira criação. É normal. O script aguarda o Terraform concluir.

---

## Custos estimados (Azure for Students — $100 de crédito)

| Recurso | SKU | Custo estimado |
|---|---|---|
| Container Apps (4 serviços) | Consumption — pay per use | ~$0–5/mês com uso leve |
| Container Registry | Basic | ~$5/mês |
| API Management | Consumption — 1M calls free | $0 para uso acadêmico |
| AI Search | Free (50 MB, 3 índices) | $0 |
| PostgreSQL Flexible | B_Standard_B1ms — 750h/mês free | $0 por 12 meses |
| Cosmos DB | Serverless — 1.000 RU/s free | $0 para uso leve |
| Azure SQL | Serverless GP_S_Gen5_1 | ~$5–15/mês |
| Static Web App | Free | $0 |
| Blob Storage | Standard LRS | ~$1/mês |

**Total estimado:** $10–25/mês, confortavelmente dentro do crédito de $100.
