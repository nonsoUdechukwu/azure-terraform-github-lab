variable "location" {
  description = "Region allowed by the training subscription."
  type        = string
  default     = "westeurope"
}

variable "learner_suffix" {
  description = "Unique non-sensitive lowercase learner label."
  type        = string
  default     = "learner01"
  validation {
    condition     = can(regex("^[a-z0-9]{3,16}$", var.learner_suffix))
    error_message = "Use 3-16 lowercase letters or digits."
  }
}

variable "vnet_purpose" {
  description = "VNet-only tag used for the drift exercise."
  type        = string
  default     = "training"
}
