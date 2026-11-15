output "subnet_names" {
  description = "Subnet names indexed by caller-supplied map key."
  value       = { for key, subnet in azurerm_subnet.this : key => subnet.name }
}
