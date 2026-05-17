#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="docai-identity-service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/../terraform" && pwd)"

die() {
  echo "[${SERVICE_NAME}] ERROR: $*" >&2
  exit 1
}

info() {
  echo "[${SERVICE_NAME}] $*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

info "Checking local prerequisites..."
require_command terraform

cd "${TERRAFORM_DIR}"

info "Formatting Terraform files..."
terraform fmt -recursive -check || die "terraform fmt failed. Run terraform fmt -recursive."

INIT_ARGS=()
if [[ -n "${TF_BACKEND_RESOURCE_GROUP:-}" ]]; then
  info "Using remote azurerm backend from environment variables."
  : "${TF_BACKEND_STORAGE_ACCOUNT:?Set TF_BACKEND_STORAGE_ACCOUNT}"
  : "${TF_BACKEND_CONTAINER:?Set TF_BACKEND_CONTAINER}"
  : "${TF_BACKEND_KEY:?Set TF_BACKEND_KEY}"
  INIT_ARGS+=(
    "-backend-config=resource_group_name=${TF_BACKEND_RESOURCE_GROUP}"
    "-backend-config=storage_account_name=${TF_BACKEND_STORAGE_ACCOUNT}"
    "-backend-config=container_name=${TF_BACKEND_CONTAINER}"
    "-backend-config=key=${TF_BACKEND_KEY}"
  )
else
  info "No TF_BACKEND_RESOURCE_GROUP set. Initializing with local state."
fi

info "Initializing Terraform..."
terraform init "${INIT_ARGS[@]}"

info "Validating Terraform..."
terraform validate

if [[ "${RUN_TERRAFORM_PLAN:-false}" == "true" ]]; then
  info "Creating plan file tfplan..."
  terraform plan -out=tfplan
else
  info "Skipping plan. Set RUN_TERRAFORM_PLAN=true to generate tfplan."
fi

info "Bootstrap completed."
