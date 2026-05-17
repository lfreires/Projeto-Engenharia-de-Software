#!/usr/bin/env bash
# bootstrap-all.sh — provisionamento completo do DocAI no Azure for Students.
# Execute no Azure Cloud Shell (shell.azure.com) após clonar o repositório.
#
# Uso:
#   export TF_VAR_sql_admin_password="SuaSenhaSQL123!"
#   export TF_VAR_postgres_admin_password="SuaSenhaPG123!"
#   bash scripts/bootstrap-all.sh
#
# O Terraform state fica salvo localmente no Cloud Shell (~/.tfstate-docai/).
# O Cloud Shell tem armazenamento persistente, então é seguro.

set -euo pipefail
trap 'echo -e "\n\033[0;31mErro na linha $LINENO — verifique o comando acima.\033[0m" >&2' ERR

# ── Configuração ──────────────────────────────────────────────────────────────

LOCATION="${LOCATION:-eastus}"
RG="${RG:-rg-docai-student}"
PREFIX="${PREFIX:-docaistudent}"

: "${TF_VAR_sql_admin_password:?'Defina TF_VAR_sql_admin_password antes de executar'}"
: "${TF_VAR_postgres_admin_password:?'Defina TF_VAR_postgres_admin_password antes de executar'}"

# Repos GitHub de cada integrante — edite antes de executar
# Formato: "usuario_github/nome_do_repo"
GITHUB_REPOS=(
  "AnaKlaussen/docai-identity-service"
  "AnaKlaussen/Project-Sophia"
  "lfreires/ingestion-service"
  "GabrielNichols/query-service"
  "GabrielNichols/DocAI-frontend"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Diretório para guardar os tfstate localmente no Cloud Shell
TF_STATE_DIR="${HOME}/.tfstate-docai"
mkdir -p "$TF_STATE_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────

log() { echo -e "\n\033[1;34m=== $* ===\033[0m"; }
ok()  { echo -e "\033[0;32m✓ $*\033[0m"; }

tf_apply() {
  local dir="$1"
  local state_file="$2"
  shift 2
  terraform -chdir="$dir" init -input=false -reconfigure \
    -backend-config="path=${state_file}"
  terraform -chdir="$dir" apply -input=false -auto-approve "${@}"
}

# ── 1. Verificar login ────────────────────────────────────────────────────────

log "Verificando login no Azure"
az account show --output table
SUB_ID=$(az account show --query id -o tsv)
TENANT_ID_LOGIN=$(az account show --query tenantId -o tsv)
az account set --subscription "$SUB_ID"
export ARM_SUBSCRIPTION_ID="$SUB_ID"
export ARM_TENANT_ID="$TENANT_ID_LOGIN"
ok "Subscription: $SUB_ID | Tenant: $TENANT_ID_LOGIN"

# ── 2. Registrar resource providers necessários ───────────────────────────────

log "Registrando resource providers (pode levar alguns minutos)"
for ns in \
  Microsoft.App \
  Microsoft.ContainerRegistry \
  Microsoft.Storage \
  Microsoft.Search \
  Microsoft.DocumentDB \
  Microsoft.DBforPostgreSQL \
  Microsoft.Sql \
  Microsoft.ApiManagement \
  Microsoft.Web \
  Microsoft.KeyVault \
  Microsoft.ManagedIdentity \
  Microsoft.OperationalInsights; do
  echo "  Registrando $ns..."
  az provider register --namespace "$ns" --subscription "$SUB_ID" --wait 2>/dev/null || \
    echo "  (aviso: não foi possível registrar $ns — Terraform tentará automaticamente)"
done
ok "Providers registrados"

# ── 3. Resource group ─────────────────────────────────────────────────────────

log "Criando resource group"
az group create --name "$RG" --location "$LOCATION" --subscription "$SUB_ID" --output none
ok "Resource group: $RG"

# ── 4. identity-service (infra compartilhada + Managed Identity) ───────────────

log "Provisionando identity-service (infra compartilhada)"

# Montar lista de repos no formato HCL para a variável
REPOS_HCL="[$(printf '"%s",' "${GITHUB_REPOS[@]}" | sed 's/,$//')]"

tf_apply "$ROOT_DIR/identity-service/terraform" \
  "$TF_STATE_DIR/identity-service.tfstate" \
  -var="sql_admin_password=${TF_VAR_sql_admin_password}" \
  -var="github_repos=${REPOS_HCL}"

# Capturar outputs do identity-service
cd "$ROOT_DIR/identity-service/terraform"
MI_CLIENT_ID=$(terraform output -raw managed_identity_client_id)
TENANT_ID=$(terraform output -raw tenant_id)
CAE_ID=$(terraform output -raw container_app_environment_id)
APIM_NAME=$(terraform output -raw api_management_name)
APIM_URL=$(terraform output -raw api_management_gateway_url)
ACR_NAME=$(terraform output -raw acr_name)
ACR_SERVER=$(terraform output -raw acr_login_server)
IDENTITY_APP_NAME=$(terraform output -raw identity_container_app_name)
IDENTITY_APP_URL=$(terraform output -raw identity_container_app_url)
cd "$ROOT_DIR"

ok "Managed Identity client_id: $MI_CLIENT_ID"
ok "ACR: $ACR_SERVER"

# ── 5. project-service ────────────────────────────────────────────────────────

log "Provisionando project-service"

tf_apply "$ROOT_DIR/project-service/terraform" \
  "$TF_STATE_DIR/project-service.tfstate" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="postgres_admin_password=${TF_VAR_postgres_admin_password}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

cd "$ROOT_DIR/project-service/terraform"
PROJECT_APP_NAME=$(terraform output -raw container_app_name)
PROJECT_APP_URL=$(terraform output -raw container_app_url)
cd "$ROOT_DIR"
ok "project-service: $PROJECT_APP_URL"

# ── 6. ingestion-service ──────────────────────────────────────────────────────

log "Provisionando ingestion-service"

INGESTION_STORAGE="${PREFIX}docs$(printf '%04x' $((RANDOM + RANDOM)))"

tf_apply "$ROOT_DIR/ingestion-service/terraform" \
  "$TF_STATE_DIR/ingestion-service.tfstate" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="storage_account_name=${INGESTION_STORAGE}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

cd "$ROOT_DIR/ingestion-service/terraform"
INGESTION_APP_NAME=$(terraform output -raw container_app_name)
INGESTION_APP_URL=$(terraform output -raw container_app_url)
cd "$ROOT_DIR"
ok "ingestion-service: $INGESTION_APP_URL"

# ── 7. query-service ──────────────────────────────────────────────────────────

log "Provisionando query-service"

tf_apply "$ROOT_DIR/query-service/terraform" \
  "$TF_STATE_DIR/query-service.tfstate" \
  -var="container_app_environment_id=${CAE_ID}" \
  -var="api_management_name=${APIM_NAME}" \
  -var="ingestion_service_url=https://${INGESTION_APP_URL}" \
  -var="container_image=mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

cd "$ROOT_DIR/query-service/terraform"
QUERY_APP_NAME=$(terraform output -raw container_app_name)
QUERY_APP_URL=$(terraform output -raw container_app_url)
cd "$ROOT_DIR"
ok "query-service: $QUERY_APP_URL"

# ── 8. frontend ───────────────────────────────────────────────────────────────

log "Provisionando frontend (Static Web App)"

tf_apply "$ROOT_DIR/frontend/terraform" \
  "$TF_STATE_DIR/frontend.tfstate"

cd "$ROOT_DIR/frontend/terraform"
FRONTEND_HOST=$(terraform output -raw default_host_name)
SWA_TOKEN=$(terraform output -raw api_key)
cd "$ROOT_DIR"
ok "Frontend: https://$FRONTEND_HOST"

# ── 9. Salvar outputs para consulta futura ────────────────────────────────────

OUTPUTS_FILE="$TF_STATE_DIR/github-secrets.txt"
cat > "$OUTPUTS_FILE" <<SECRETS

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
SECRETS

cat "$OUTPUTS_FILE"
echo ""
echo "Este arquivo também foi salvo em: $OUTPUTS_FILE"
echo "Para ver novamente: cat $OUTPUTS_FILE"
