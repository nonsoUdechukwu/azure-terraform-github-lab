mock_provider "azurerm" {}

run "builds_network" {
  command = plan

  variables {
    name                = "vnet-tflab-test"
    resource_group_name = "rg-tflab-test"
    location            = "westeurope"
    address_space       = ["10.42.0.0/16"]
    tags                = { purpose = "training" }
    subnets = {
      app  = { name = "snet-app", address_prefixes = ["10.42.1.0/24"] }
      data = { name = "snet-data", address_prefixes = ["10.42.2.0/24"] }
    }
  }

  assert {
    condition     = toset(keys(azurerm_subnet.this)) == toset(["app", "data"])
    error_message = "Each supplied subnet key must create a subnet."
  }

  assert {
    condition     = azurerm_subnet.this["app"].address_prefixes == tolist(["10.42.1.0/24"])
    error_message = "The app subnet must retain its CIDR."
  }

  assert {
    condition     = alltrue([for subnet in azurerm_subnet.this : subnet.default_outbound_access_enabled == false])
    error_message = "Implicit default outbound access must be disabled."
  }

  assert {
    condition     = azurerm_virtual_network.this.tags["purpose"] == "training"
    error_message = "The VNet must receive tags."
  }
}
