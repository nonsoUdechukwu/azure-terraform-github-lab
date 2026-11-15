variable "name" {
  description = "Virtual-network name."
  type        = string
}

variable "resource_group_name" {
  description = "Existing resource-group name, normally a module output."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "address_space" {
  description = "IPv4 CIDR blocks for the VNet."
  type        = list(string)
}

variable "subnets" {
  description = "Stable map keys become subnet resource instance keys."
  type = map(object({
    name             = string
    address_prefixes = list(string)
  }))
}

variable "tags" {
  description = "Tags for the VNet; Azure subnets do not support tags."
  type        = map(string)
  default     = {}
}
