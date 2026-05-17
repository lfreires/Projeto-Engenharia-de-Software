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

variable "postgres_admin_login" {
  type        = string
  description = "PostgreSQL admin login."
  default     = "docaiadmin"
}

variable "postgres_admin_password" {
  type        = string
  description = "PostgreSQL admin password. Provide through TF_VAR_postgres_admin_password."
  sensitive   = true
}

variable "container_image" {
  type        = string
  description = "Project service image pushed by CD."
}

resource "azurerm_postgresql_flexible_server" "projects" {
  name                   = "docai-projects-pg"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  administrator_login    = var.postgres_admin_login
  administrator_password = var.postgres_admin_password
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
  zone                   = "1"
}

resource "azurerm_postgresql_flexible_server_database" "projects" {
  name      = "docai_projects"
  server_id = azurerm_postgresql_flexible_server.projects.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_container_app" "projects" {
  name                         = "docai-project-service"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = var.container_app_environment_id
  revision_mode                = "Single"

  template {
    container {
      name   = "projects"
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

resource "azurerm_api_management_api" "projects" {
  name                = "docai-projects"
  resource_group_name = var.resource_group_name
  api_management_name = var.api_management_name
  revision            = "1"
  display_name        = "DocAI Projects"
  path                = "api/v1/projects"
  protocols           = ["https"]
}

output "database_engine" {
  value = "postgresql-flexible-server"
}

output "container_app_url" {
  value = azurerm_container_app.projects.latest_revision_fqdn
}
