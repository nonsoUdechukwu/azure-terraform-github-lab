# Resource-group module v1.0.0

Creates one Azure resource group. Configure the AzureRM provider in the calling
root, not here. Requires Terraform >=1.15.3,<2 and AzureRM >=4.50.0,<5.

| Input | Type | Required/default |
|---|---|---|
| name | string | Required |
| location | string | Required |
| tags | map(string) | `{}` |

Outputs: `name`, `location`, `id`.

```hcl
module "resource_group" {
  source   = "git::https://github.com/YOUR_GITHUB_USER/terraform-azurerm-resource-group.git?ref=v1.0.0"
  name     = "rg-tflab-dev-learner01"
  location = "westeurope"
  tags     = { environment = "dev" }
}
```

Run `terraform init -backend=false`, `terraform validate` and `terraform test`.
Tests use a mocked provider and do not create Azure resources.
