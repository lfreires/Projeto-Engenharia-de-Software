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
  description = "Azure region for the Static Web App."
  default     = "eastus2"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group created by identity-service."
  default     = "rg-docai-student"
}

resource "azurerm_static_web_app" "frontend" {
  name                = "docai-frontend"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_tier            = "Free"
  sku_size            = "Free"
}

output "default_host_name" {
  value = azurerm_static_web_app.frontend.default_host_name
}

output "api_key" {
  value     = azurerm_static_web_app.frontend.api_key
  sensitive = true
}
