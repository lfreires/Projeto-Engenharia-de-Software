terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  # Remote state in Azure Blob — bootstrap with scripts/terraform-bootstrap.sh
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

# ── Resource Group ─────────────────────────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# ── Container Registry ─────────────────────────────────────────────────────────
resource "azurerm_container_registry" "acr" {
  name                = "${var.project_prefix}docaiacr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

# ── Storage Account (chunks + metadata + terraform state) ─────────────────────
resource "azurerm_storage_account" "main" {
  name                     = "${var.project_prefix}docaistorage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "chunks" {
  name                  = "chunks"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# ── Azure AI Search (Free — 50 MB, 3 indices) ──────────────────────────────────
resource "azurerm_search_service" "main" {
  name                = "${var.project_prefix}-docai-search"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "free"
}

# ── Key Vault ──────────────────────────────────────────────────────────────────
resource "azurerm_key_vault" "main" {
  name                       = "${var.project_prefix}-docai-kv"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = ["Get", "List", "Set", "Delete"]
  }
}

resource "azurerm_key_vault_secret" "groq_key" {
  name         = "groq-api-key"
  value        = var.groq_api_key
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "bearer_token" {
  name         = "bearer-token"
  value        = var.bearer_token
  key_vault_id = azurerm_key_vault.main.id
}

# ── Log Analytics (required for Container Apps) ────────────────────────────────
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project_prefix}-docai-logs"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# ── Container Apps Environment ─────────────────────────────────────────────────
resource "azurerm_container_app_environment" "main" {
  name                       = "${var.project_prefix}-docai-env"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

# ── Backend Container App (query-service) ─────────────────────────────────────
resource "azurerm_container_app" "backend" {
  name                         = "${var.project_prefix}-query-service"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }
  secret {
    name  = "groq-api-key"
    value = var.groq_api_key
  }
  secret {
    name  = "azure-search-key"
    value = var.azure_search_key
  }
  secret {
    name  = "bearer-token"
    value = var.bearer_token
  }

  template {
    min_replicas = 0
    max_replicas = 3

    container {
      name  = "query-service"
      image = "${azurerm_container_registry.acr.login_server}/${var.backend_image}"
      # sentence-transformers needs ~80 MB RAM to load the embedding model
      cpu    = 0.5
      memory = "1.5Gi"

      env {
        name        = "GROQ_API_KEY"
        secret_name = "groq-api-key"
      }
      env {
        name        = "AZURE_SEARCH_KEY"
        secret_name = "azure-search-key"
      }
      env {
        name  = "AZURE_SEARCH_ENDPOINT"
        value = "https://${azurerm_search_service.main.name}.search.windows.net"
      }
      env {
        name  = "AZURE_SEARCH_INDEX"
        value = "documents"
      }
      env {
        name  = "PRIMARY_LLM_MODEL"
        value = "llama-3.3-70b-versatile"
      }
      env {
        name  = "FALLBACK_LLM_MODEL"
        value = "llama-3.1-8b-instant"
      }
      env {
        name        = "BEARER_TOKEN"
        secret_name = "bearer-token"
      }

      liveness_probe {
        path             = "/api/v1/query/health"
        port             = 8000
        transport        = "HTTP"
        initial_delay    = 15
        interval_seconds = 30
      }

      readiness_probe {
        path             = "/api/v1/query/health"
        port             = 8000
        transport        = "HTTP"
        initial_delay    = 10
        interval_seconds = 10
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

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }
}

# ── Frontend Container App ─────────────────────────────────────────────────────
resource "azurerm_container_app" "frontend" {
  name                         = "${var.project_prefix}-query-frontend"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  template {
    min_replicas = 0
    max_replicas = 2

    container {
      name   = "query-frontend"
      image  = "${azurerm_container_registry.acr.login_server}/${var.frontend_image}"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }
}
