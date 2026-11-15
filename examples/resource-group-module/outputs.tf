output "name" {
  description = "Resource-group name for downstream modules."
  value       = azurerm_resource_group.this.name
}

output "location" {
  description = "Normalized Azure location."
  value       = azurerm_resource_group.this.location
}

output "id" {
  description = "Azure resource-group ID."
  value       = azurerm_resource_group.this.id
}
