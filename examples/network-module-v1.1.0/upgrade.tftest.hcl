mock_provider "azurerm" {}

run "exposes_subnet_names" {
  command = plan

  variables {
    name                = "vnet-tflab-test"
    resource_group_name = "rg-tflab-test"
    location            = "westeurope"
    address_space       = ["10.42.0.0/16"]
    subnets = {
      app  = { name = "snet-app", address_prefixes = ["10.42.1.0/24"] }
      data = { name = "snet-data", address_prefixes = ["10.42.2.0/24"] }
    }
  }

  assert {
    condition     = tomap(output.subnet_names) == tomap({ app = "snet-app", data = "snet-data" })
    error_message = "The new output must expose names with stable input keys."
  }
}
