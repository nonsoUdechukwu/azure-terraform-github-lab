output "resource_group_name" {
  description = "Created resource-group name."
  value       = module.resource_group.name
}

output "vnet_id" {
  description = "Created VNet ID; do not post subscription identifiers publicly."
  value       = module.network.vnet_id
}

output "subnet_ids" {
  description = "Created subnet IDs by logical key."
  value       = module.network.subnet_ids
}
