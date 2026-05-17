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

variable "container_image" {
  type        = string
  description = "Query service image pushed by CD."
}

variable "ingestion_service_url" {
  type        = string
  description = "Internal ingestion-service URL used by query-service."
}

resource "azurerm_cosmosdb_account" "query" {
  name                = "docai-query-cosmos"
  resource_group_name = var.resource_group_name
  location            = var.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }
}

resource "azurerm_cosmosdb_sql_database" "query" {
  name                = "docai_query"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.query.name
}

resource "azurerm_container_app" "query" {
  name                         = "docai-query-service"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = var.container_app_environment_id
  revision_mode                = "Single"

  template {
    container {
      name   = "query"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "INGESTION_SERVICE_URL"
        value = var.ingestion_service_url
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
}

resource "azurerm_api_management_api" "query" {
  name                = "docai-query"
  resource_group_name = var.resource_group_name
  api_management_name = var.api_management_name
  revision            = "1"
  display_name        = "DocAI Query"
  path                = "api/v1/query"
  protocols           = ["https"]
}

output "database_engine" {
  value = "cosmos-db-nosql"
}

output "container_app_name" {
  value = azurerm_container_app.query.name
}

output "container_app_url" {
  value = azurerm_container_app.query.latest_revision_fqdn
}
