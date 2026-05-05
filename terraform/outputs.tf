output "backend_url" {
  description = "URL pública do backend (query-service)"
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "frontend_url" {
  description = "URL pública do frontend"
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "acr_login_server" {
  description = "Login server do Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "Admin username do ACR (usar como DOCKER_USERNAME no CI)"
  value       = azurerm_container_registry.acr.admin_username
}

output "search_endpoint" {
  description = "Endpoint do Azure AI Search"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "storage_account_name" {
  description = "Nome da Storage Account (para Ingestion module)"
  value       = azurerm_storage_account.main.name
}

output "resource_group_name" {
  description = "Nome do Resource Group"
  value       = azurerm_resource_group.main.name
}
