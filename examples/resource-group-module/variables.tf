variable "name" {
  description = "Name of the resource group."
  type        = string
}

variable "location" {
  description = "Azure region, for example westeurope."
  type        = string
}

variable "tags" {
  description = "Non-sensitive Azure resource tags."
  type        = map(string)
  default     = {}
}
