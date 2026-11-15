locals {
  common_tags = {
    project     = "terraform-lab"
    environment = "dev"
    owner       = "learner-demo"
    cost_center = "training"
    managed_by  = "terraform"
  }
}

module "resource_group" {
  source = "git::https://github.com/YOUR_GITHUB_USER/terraform-azurerm-resource-group.git?ref=v1.0.0"

  name     = "rg-tflab-dev-${var.learner_suffix}"
  location = var.location
  tags     = local.common_tags
}

module "network" {
  source = "git::https://github.com/YOUR_GITHUB_USER/terraform-azurerm-network.git?ref=v1.0.0"

  name                = "vnet-tflab-dev-${var.learner_suffix}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  address_space       = ["10.42.0.0/16"]
  tags                = merge(local.common_tags, { purpose = var.vnet_purpose })
  subnets = {
    app  = { name = "snet-app", address_prefixes = ["10.42.1.0/24"] }
    data = { name = "snet-data", address_prefixes = ["10.42.2.0/24"] }
  }
}
