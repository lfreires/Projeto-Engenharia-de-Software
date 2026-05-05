#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap do Terraform state remoto no Azure (executar UMA VEZ antes do
# primeiro `terraform init`)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PREFIX="${PROJECT_PREFIX:-mack}"
LOCATION="${AZURE_LOCATION:-eastus}"
TF_RG="rg-tfstate"
TF_SA="${PREFIX}tfstate"
TF_CONTAINER="tfstate"
TF_KEY="docai.tfstate"

echo "→ Fazendo login no Azure..."
az login
az account set --subscription "${AZURE_SUBSCRIPTION_ID}"

echo "→ Criando Resource Group para Terraform state: $TF_RG"
az group create -n "$TF_RG" -l "$LOCATION"

echo "→ Criando Storage Account: $TF_SA"
az storage account create -n "$TF_SA" -g "$TF_RG" -l "$LOCATION" --sku Standard_LRS

echo "→ Criando container: $TF_CONTAINER"
az storage container create -n "$TF_CONTAINER" --account-name "$TF_SA"

echo ""
echo "✓ Bootstrap concluído. Execute agora:"
echo ""
echo "  cd terraform/"
echo "  terraform init \\"
echo "    -backend-config=\"resource_group_name=$TF_RG\" \\"
echo "    -backend-config=\"storage_account_name=$TF_SA\" \\"
echo "    -backend-config=\"container_name=$TF_CONTAINER\" \\"
echo "    -backend-config=\"key=$TF_KEY\""
echo ""
echo "  cp terraform.tfvars.example terraform.tfvars  # preencher valores"
echo "  terraform plan -var-file=terraform.tfvars"
echo "  terraform apply -var-file=terraform.tfvars -auto-approve"
