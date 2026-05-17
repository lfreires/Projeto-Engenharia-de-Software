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

data "azurerm_client_config" "current" {}

variable "location" {
  type        = string
  description = "Azure region for the student-cost environment."
  default     = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "Shared resource group created first by identity-service."
  default     = "rg-docai-student"
}

variable "name_prefix" {
  type        = string
  description = "Short prefix used for globally named resources."
  default     = "docaistudent"
}

variable "sql_admin_login" {
  type        = string
  description = "Azure SQL admin login for the identity database."
  default     = "docaiadmin"
}

variable "sql_admin_password" {
  type        = string
  description = "Azure SQL admin password. Provide through TF_VAR_sql_admin_password."
  sensitive   = true
}

variable "container_image" {
  type        = string
  description = "Identity service image pushed by CD."
  default     = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
}

resource "azurerm_resource_group" "docai" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "shared" {
  name                = "${var.name_prefix}acr"
  resource_group_name = azurerm_resource_group.docai.name
  location            = azurerm_resource_group.docai.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_log_analytics_workspace" "shared" {
  name                = "${var.name_prefix}-logs"
  resource_group_name = azurerm_resource_group.docai.name
  location            = azurerm_resource_group.docai.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "shared" {
  name                       = "${var.name_prefix}-cae"
  resource_group_name        = azurerm_resource_group.docai.name
  location                   = azurerm_resource_group.docai.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.shared.id
}

resource "azurerm_api_management" "gateway" {
  name                = "${var.name_prefix}-apim"
  resource_group_name = azurerm_resource_group.docai.name
  location            = azurerm_resource_group.docai.location
  publisher_name      = "DocAI Student"
  publisher_email     = "admin@example.com"
  sku_name            = "Consumption_0"
}

resource "azurerm_key_vault" "shared" {
  name                      = "${var.name_prefix}-kv"
  resource_group_name       = azurerm_resource_group.docai.name
  location                  = azurerm_resource_group.docai.location
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
}

resource "azurerm_mssql_server" "identity" {
  name                         = "${var.name_prefix}-identity-sql"
  resource_group_name          = azurerm_resource_group.docai.name
  location                     = azurerm_resource_group.docai.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"
}

resource "azurerm_mssql_database" "identity" {
  name                        = "docai_identity"
  server_id                   = azurerm_mssql_server.identity.id
  sku_name                    = "GP_S_Gen5_1"
  min_capacity                = 0.5
  auto_pause_delay_in_minutes = 60
}

resource "azurerm_container_app" "identity" {
  name                         = "docai-identity-service"
  resource_group_name          = azurerm_resource_group.docai.name
  container_app_environment_id = azurerm_container_app_environment.shared.id
  revision_mode                = "Single"

  template {
    container {
      name   = "identity"
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

output "resource_group_name" {
  value = azurerm_resource_group.docai.name
}

output "acr_login_server" {
  value = azurerm_container_registry.shared.login_server
}

output "container_app_environment_id" {
  value = azurerm_container_app_environment.shared.id
}

output "api_management_name" {
  value = azurerm_api_management.gateway.name
}
