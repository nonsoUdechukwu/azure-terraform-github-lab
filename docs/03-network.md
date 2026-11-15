# 03 - Author your network module

[Previous](02-resource-group.md) | [Course index](../README.md) | [Next](04-publish.md)

## Objectives

Build a VNet and a caller-defined map of subnets. Understand `for_each`, stable
resource addresses and implicit dependencies.

## 1. Create the contract

```bash
cd "$LAB_HOME/terraform-azurerm-network"
mkdir -p tests .github/workflows
```

Author these complete reference files in **your module repo root**:

| Destination | Reference and what to learn |
|---|---|
| `versions.tf` | [Requirements](../examples/network-module/versions.tf): no provider credentials |
| `variables.tf` | [Inputs](../examples/network-module/variables.tf): required VNet/RG/region, CIDR list, subnet map, optional tags |
| `main.tf` | [Resources](../examples/network-module/main.tf): VNet plus standalone subnets |
| `outputs.tf` | [Outputs](../examples/network-module/outputs.tf): `vnet_id` and `subnet_ids` only |
| `tests/network.tftest.hcl` | [Mock test](../examples/network-module/tests/network.tftest.hcl): two subnets and disabled implicit outbound |
| `README.md` | [Consumer docs](../examples/network-module/README.md): inputs, outputs, compatibility |

Read/type the files, or use these precise copies and then explain every block:

```bash
cp "$COURSE"/examples/network-module/*.tf .
cp "$COURSE/examples/network-module/tests/network.tftest.hcl" tests/
cp "$COURSE/examples/network-module/README.md" README.md
cp "$COURSE/templates/module-ci.yml" .github/workflows/ci.yml
```

Replace the README's course-relative caller link with
`https://github.com/YOUR_GITHUB_USER/azure-platform-live/tree/main/environments/dev`
(substitute your username). This link will resolve after lesson 05.
Do **not** copy `network-module-v1.1.0` yet. That directory is a later release
delta, not part of v1.0.0.

## 2. Trace the dependencies

The VNet uses the input resource-group name. Every subnet refers to
`azurerm_virtual_network.this.name`, so Terraform creates the VNet first.
No explicit `depends_on` is needed. Later the root will pass
`module.resource_group.name`, linking this module to the resource-group module.

The subnet map looks like:

```hcl
subnets = {
  app  = { name = "snet-app", address_prefixes = ["10.42.1.0/24"] }
  data = { name = "snet-data", address_prefixes = ["10.42.2.0/24"] }
}
```

`for_each = var.subnets` creates addresses such as
`azurerm_subnet.this["app"]`. Preserve keys once deployed; changing a key changes
Terraform's identity even if the Azure name is unchanged. A future real rename
may need a reviewed `moved` block, not casual deletion/recreation.

The `10.42.0.0/16` VNet contains the two non-overlapping `/24` subnets.
Do not copy these ranges into a connected corporate network without checking
overlap. Azure subnets cannot receive resource tags; only the VNet gets `tags`.
`default_outbound_access_enabled = false` makes the empty lab's intent explicit;
this is not a complete outbound-connectivity design for future workloads.

**Never mix** inline VNet `subnet {}` blocks and `azurerm_subnet` resources
managing the same VNet.

## 3. Validate, test, commit and push

```bash
terraform fmt -recursive
terraform init -backend=false
terraform validate
terraform test
git status --short
git add .gitignore README.md versions.tf variables.tf main.tf outputs.tf tests .github
git diff --cached
git commit -m "Create network module with standalone subnets"
git push -u origin main
```

Expected: `1 passed, 0 failed`; CI passes. Nothing exists in Azure.

## Checkpoint and exercise

Explain why the test can verify `subnet_ids` keys but not real Azure ID values
at plan time. Many IDs are unknown until apply.

**Exercise:** In the test only, add a third subnet. Observe the existing
two-key assertion fail. Update the assertion for your experiment, rerun, then
restore the published baseline before continuing. Describe how you'd document
this input without making every caller create three subnets.

[Previous](02-resource-group.md) | [Course index](../README.md) | [Next](04-publish.md)
