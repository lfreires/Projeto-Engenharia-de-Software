#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="docai-frontend"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/../terraform" && pwd)"

die() {
  echo "[${SERVICE_NAME}] ERROR: $*" >&2
  exit 1
}

info() {
  echo "[${SERVICE_NAME}] $*"
}

command -v terraform >/dev/null 2>&1 || die "Missing required command: terraform"

cd "${TERRAFORM_DIR}"
info "Checking Terraform formatting..."
terraform fmt -recursive -check || die "terraform fmt failed. Run terraform fmt -recursive."

info "Initializing Terraform..."
terraform init

info "Validating Terraform..."
terraform validate

if [[ "${RUN_TERRAFORM_PLAN:-false}" == "true" ]]; then
  terraform plan -out=tfplan
else
  info "Skipping plan. Set RUN_TERRAFORM_PLAN=true to generate tfplan."
fi
