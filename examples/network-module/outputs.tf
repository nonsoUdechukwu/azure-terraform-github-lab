output "vnet_id" {
  description = "Virtual-network ID."
  value       = azurerm_virtual_network.this.id
}

output "subnet_ids" {
  description = "Subnet IDs indexed by caller-supplied map key."
  value       = { for key, subnet in azurerm_subnet.this : key => subnet.id }
}
