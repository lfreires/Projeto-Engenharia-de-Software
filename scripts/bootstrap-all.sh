#!/usr/bin/env bash
# bootstrap-all.sh — provisionamento completo do DocAI no Azure for Students.
# Execute uma única vez, localmente, após: az login
#
# Uso:
#   export TF_VAR_sql_admin_password="SuaSenhaSQL123!"
#   export TF_VAR_postgres_admin_password="SuaSenhaPG123!"
#   bash scripts/bootstrap-all.sh
#
# Variáveis opcionais (têm padrão):
#   LOCATION          — região Azure (padrão: eastus)
#   RG                — nome do resource group (padrão: rg-docai-student)
#   PREFIX            — prefixo de recursos (padrão: docaistudent)
#   STORAGE_SUFFIX    — sufixo único p/ storage account do tfstate (padrão: gerado automaticamente)

set -euo pipefail

# ── Configuração ──────────────────────────────────────────────────────────────

LOCATION="${LOCATION:-eastus}"
RG="${RG:-rg-docai-student}"
PREFIX="${PREFIX:-docaistudent}"

: "${TF_VAR_sql_admin_password:?'Defina TF_VAR_sql_admin_password antes de executar'}"
: "${TF_VAR_postgres_admin_password:?'Defina TF_VAR_postgres_admin_password antes de executar'}"

# Repos GitHub de cada integrante — edite antes de executar
# Formato: "usuario_github/nome_do_repo"
GITHUB_REPOS=(
  "GITHUB_USER_1/docai-identity-service"
  "GITHUB_USER_2/docai-project-service"
  "GITHUB_USER_3/docai-ingestion-service"
  "GITHUB_USER_4/docai-query-service"
  "GITHUB_USER_1/docai-frontend"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Helpers ───────────────────────────────────────────────────────────────────

log() { echo -e "\n\033[1;34m=== $* ===\033[0m"; }
ok()  { echo -e "\033[0;32m✓ $*\033[0m"; }

tf_apply() {
  local dir="$1"; shift
  terraform -chdir="$dir" init -input=false "${@}" -reconfigure
  terraform -chdir="$dir" apply -input=false -auto-approve "${@}"
}

# ── 1. Verificar login ────────────────────────────────────────────────────────

log "Verificando login no Azure"
az account show --output table
SUB_ID=$(az account show --query id -o tsv)
ok "Subscription: $SUB_ID"

# ── 2. Storage account para Terraform state ───────────────────────────────────

log "Criando storage account para Terraform state"

STORAGE_SUFFIX="${STORAGE_SUFFIX:-$(tr -dc 'a-z0-9' </dev/urandom | head -c 6)}"
TF_STORAGE="${PREFIX}tfstate${STORAGE_SUFFIX}"
TF_CONTAINER="tfstate"

az group create --name "$RG" --location "$LOCATION" --output none
az storage account create \
  --name "$TF_STORAGE" \
  --resource-group "$RG" \
  --sku Standard_LRS \
  --allow-blob-public-access false \
  --output none
az storage container create \
  --name "$TF_CONTAINER" \
  --account-name "$TF_STORAGE" \
  --output none

ok "Storage account: $TF_STORAGE"

# Exportar variáveis de backend para todos os serviços
export TF_BACKEND_RESOURCE_GROUP="$RG"
export TF_BACKEND_STORAGE_ACCOUNT="$TF_STORAGE"
export TF_BACKEND_CONTAINER="$TF_CONTAINER"

# ── 3. identity-service (infra compartilhada + Managed Identity) ───────────────

log "Provisionando identity-service (infra compartilhada)"

export TF_BACKEND_KEY="identity-service.tfstate"

# Montar lista de repos no formato HCL para a variável
REPOS_HCL="[$(printf '"%s",' "${GITHUB_REPOS[@]}" | sed 's/,$//')]"

BACKEND_ARGS=(
  -backend-config="resource_group_name=${TF_BACKEND_RESOURCE_GROUP}"
  -backend-config="storage_account_name=${TF_BACKEND_STORAGE_ACCOUNT}"
  -backend-config="container_name=${TF_BACKEND_CONTAINER}"
  -backend-config="key=${TF_BACKEND_KEY}"
)

tf_apply "$ROOT_DIR/identity-service/terraform" \
  "${BACKEND_ARGS[@]}" \
  -var="sql_admin_password=${TF_VAR_sql_admin_password}" \
  -var="github_repos=${REPOS_HCL}"

# Capturar outputs do identity-service
MI_CLIENT_ID=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw managed_identity_client_id)
TENANT_ID=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw tenant_id)
CAE_ID=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw container_app_environment_id)
APIM_NAME=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw api_management_name)
APIM_URL=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw api_management_gateway_url)
ACR_NAME=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw acr_name)
ACR_SERVER=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw acr_login_server)
IDENTITY_APP_NAME=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw identity_container_app_name)
IDENTITY_APP_URL=$(terraform -chdir="$ROOT_DIR/identity-service/terraform" output -raw identity_container_app_url)

ok "Managed Identity client_id: $MI_CLIENT_ID"
ok "ACR: $ACR_SERVER"

# ── 4. project-service ────────────────────────────────────────────────────────

log "Provisionando project-service"

export TF_BACKEND_KEY="project-service.tfstate"
BACKEND_ARGS[-1]="-backend-config=key=${TF_BACKEND_KEY}"

tf_apply "$ROOT_DIR/project-service/terraform" \
  "${BACKEND_ARGS[@]}" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="postgres_admin_password=${TF_VAR_postgres_admin_password}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

PROJECT_APP_NAME=$(terraform -chdir="$ROOT_DIR/project-service/terraform" output -raw container_app_name)
PROJECT_APP_URL=$(terraform -chdir="$ROOT_DIR/project-service/terraform" output -raw container_app_url)
ok "project-service: $PROJECT_APP_URL"

# ── 5. ingestion-service ──────────────────────────────────────────────────────

log "Provisionando ingestion-service"

export TF_BACKEND_KEY="ingestion-service.tfstate"
BACKEND_ARGS[-1]="-backend-config=key=${TF_BACKEND_KEY}"

# Nome do storage account para documentos (globalmente único)
INGESTION_STORAGE="${PREFIX}docs$(tr -dc 'a-z0-9' </dev/urandom | head -c 4)"

tf_apply "$ROOT_DIR/ingestion-service/terraform" \
  "${BACKEND_ARGS[@]}" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="storage_account_name=${INGESTION_STORAGE}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

INGESTION_APP_NAME=$(terraform -chdir="$ROOT_DIR/ingestion-service/terraform" output -raw container_app_name)
INGESTION_APP_URL=$(terraform -chdir="$ROOT_DIR/ingestion-service/terraform" output -raw container_app_url)
ok "ingestion-service: $INGESTION_APP_URL"

# ── 6. query-service ──────────────────────────────────────────────────────────

log "Provisionando query-service"

export TF_BACKEND_KEY="query-service.tfstate"
BACKEND_ARGS[-1]="-backend-config=key=${TF_BACKEND_KEY}"

tf_apply "$ROOT_DIR/query-service/terraform" \
  "${BACKEND_ARGS[@]}" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="ingestion_service_url=https://${INGESTION_APP_URL}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

QUERY_APP_NAME=$(terraform -chdir="$ROOT_DIR/query-service/terraform" output -raw container_app_name)
QUERY_APP_URL=$(terraform -chdir="$ROOT_DIR/query-service/terraform" output -raw container_app_url)
ok "query-service: $QUERY_APP_URL"

# ── 7. frontend ───────────────────────────────────────────────────────────────

log "Provisionando frontend (Static Web App)"

tf_apply "$ROOT_DIR/frontend/terraform"

FRONTEND_HOST=$(terraform -chdir="$ROOT_DIR/frontend/terraform" output -raw default_host_name)
SWA_TOKEN=$(terraform -chdir="$ROOT_DIR/frontend/terraform" output -raw api_key)
ok "Frontend: https://$FRONTEND_HOST"

# ── 8. Imprimir guia de configuração dos GitHub Secrets ───────────────────────

cat <<EOF


╔══════════════════════════════════════════════════════════════════════════════╗
║          GUIA DE CONFIGURAÇÃO DOS REPOSITÓRIOS GITHUB                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Os 3 secrets abaixo são IGUAIS para todos os 4 repositórios de backend:

  AZURE_CLIENT_ID       = ${MI_CLIENT_ID}
  AZURE_TENANT_ID       = ${TENANT_ID}
  AZURE_SUBSCRIPTION_ID = ${SUB_ID}

────────────────────────────────────────────────────────────────────────────────
IDENTITY-SERVICE  (repo: ${GITHUB_REPOS[0]})
────────────────────────────────────────────────────────────────────────────────
  GitHub > Settings > Environments > production > Secrets:
    AZURE_CLIENT_ID       = ${MI_CLIENT_ID}
    AZURE_TENANT_ID       = ${TENANT_ID}
    AZURE_SUBSCRIPTION_ID = ${SUB_ID}

  GitHub > Settings > Environments > production > Variables:
    ACR_NAME              = ${ACR_NAME}
    ACR_LOGIN_SERVER      = ${ACR_SERVER}
    CONTAINER_APP_NAME    = ${IDENTITY_APP_NAME}
    RESOURCE_GROUP        = ${RG}
    HEALTH_URL            = https://${IDENTITY_APP_URL}/health

────────────────────────────────────────────────────────────────────────────────
PROJECT-SERVICE  (repo: ${GITHUB_REPOS[1]})
────────────────────────────────────────────────────────────────────────────────
  Secrets: (iguais ao identity-service)
  Variables:
    ACR_NAME              = ${ACR_NAME}
    ACR_LOGIN_SERVER      = ${ACR_SERVER}
    CONTAINER_APP_NAME    = ${PROJECT_APP_NAME}
    RESOURCE_GROUP        = ${RG}
    HEALTH_URL            = https://${PROJECT_APP_URL}/health

────────────────────────────────────────────────────────────────────────────────
INGESTION-SERVICE  (repo: ${GITHUB_REPOS[2]})
────────────────────────────────────────────────────────────────────────────────
  Secrets: (iguais ao identity-service)
  Variables:
    ACR_NAME              = ${ACR_NAME}
    ACR_LOGIN_SERVER      = ${ACR_SERVER}
    CONTAINER_APP_NAME    = ${INGESTION_APP_NAME}
    RESOURCE_GROUP        = ${RG}
    HEALTH_URL            = https://${INGESTION_APP_URL}/health

────────────────────────────────────────────────────────────────────────────────
QUERY-SERVICE  (repo: ${GITHUB_REPOS[3]})
────────────────────────────────────────────────────────────────────────────────
  Secrets: (iguais ao identity-service)
  Variables:
    ACR_NAME              = ${ACR_NAME}
    ACR_LOGIN_SERVER      = ${ACR_SERVER}
    CONTAINER_APP_NAME    = ${QUERY_APP_NAME}
    RESOURCE_GROUP        = ${RG}
    HEALTH_URL            = https://${QUERY_APP_URL}/health

────────────────────────────────────────────────────────────────────────────────
FRONTEND  (repo: ${GITHUB_REPOS[4]})
────────────────────────────────────────────────────────────────────────────────
  Secrets:
    AZURE_STATIC_WEB_APPS_API_TOKEN = ${SWA_TOKEN}
    VITE_BEARER_TOKEN               = dev-token

  Variables:
    VITE_API_BASE_URL   = ${APIM_URL}
    VITE_PROJECT_ID     = proj-demo

════════════════════════════════════════════════════════════════════════════════
Bootstrap concluído! Salve o output acima antes de fechar o terminal.
════════════════════════════════════════════════════════════════════════════════
EOF
