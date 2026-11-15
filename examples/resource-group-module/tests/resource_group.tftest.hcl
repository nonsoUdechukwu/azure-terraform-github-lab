mock_provider "azurerm" {}

run "preserves_inputs" {
  command = plan

  variables {
    name     = "rg-tflab-test"
    location = "westeurope"
    tags     = { environment = "test" }
  }

  assert {
    condition     = output.name == "rg-tflab-test"
    error_message = "The module must expose the resource-group name."
  }

  assert {
    condition     = azurerm_resource_group.this.tags["environment"] == "test"
    error_message = "The module must propagate resource tags."
  }
}
