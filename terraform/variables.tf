variable "resource_group_name" {
  description = "Nome do Resource Group"
  type        = string
  default     = "rg-docai-prod"
}

variable "location" {
  description = "Região Azure"
  type        = string
  default     = "eastus"
}

variable "project_prefix" {
  description = "Prefixo único para nomes de recursos (sem traços, max 8 chars)"
  type        = string
  default     = "mack"
}

variable "groq_api_key" {
  description = "Groq API Key (free tier — console.groq.com)"
  type        = string
  sensitive   = true
}

variable "azure_search_key" {
  description = "Azure AI Search Admin Key (gerado após provisionamento do Search Service)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bearer_token" {
  description = "Token Bearer simples para autenticação interna entre frontend e backend"
  type        = string
  sensitive   = true
  default     = "change-me-in-prod"
}

variable "vite_project_id" {
  description = "ID do projeto que o frontend consultará por padrão"
  type        = string
  default     = "ecommerce-api"
}

variable "backend_image" {
  description = "Imagem do backend no ACR (sem registry prefix)"
  type        = string
  default     = "query-service:latest"
}

variable "frontend_image" {
  description = "Imagem do frontend no ACR (sem registry prefix)"
  type        = string
  default     = "query-frontend:latest"
}
