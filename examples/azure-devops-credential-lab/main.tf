terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.49.0"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}

variable "resource_group_name" {
  type = string
}

resource "azurerm_resource_group" "demo" {
  name     = var.resource_group_name
  location = "westeurope"
}
