terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  type        = string
  description = "Azure region matching the shared DocAI resource group."
  default     = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group created by identity-service."
  default     = "rg-docai-student"
}

variable "container_app_environment_id" {
  type        = string
  description = "Shared Container Apps Environment ID from identity-service output."
}

variable "api_management_name" {
  type        = string
  description = "Shared APIM instance name from identity-service output."
}

variable "storage_account_name" {
  type        = string
  description = "Globally unique storage account name for uploaded documents and chunks."
}

variable "container_image" {
  type        = string
  description = "Ingestion service image pushed by CD."
}

resource "azurerm_storage_account" "documents" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "documents" {
  name                  = "documents"
  storage_account_name  = azurerm_storage_account.documents.name
  container_access_type = "private"
}

resource "azurerm_search_service" "vector" {
  name                = "docai-ingestion-search"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "free"
  replica_count       = 1
  partition_count     = 1
}

resource "azurerm_container_app" "ingestion" {
  name                         = "docai-ingestion-service"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = var.container_app_environment_id
  revision_mode                = "Single"

  template {
    container {
      name   = "ingestion"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"
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
}

resource "azurerm_api_management_api" "ingestion" {
  name                = "docai-ingestion"
  resource_group_name = var.resource_group_name
  api_management_name = var.api_management_name
  revision            = "1"
  display_name        = "DocAI Ingestion"
  path                = "api/v1/ingestion"
  protocols           = ["https"]
}

output "search_tier" {
  value = azurerm_search_service.vector.sku
}

output "container_app_name" {
  value = azurerm_container_app.ingestion.name
}

output "container_app_url" {
  value = azurerm_container_app.ingestion.latest_revision_fqdn
}
