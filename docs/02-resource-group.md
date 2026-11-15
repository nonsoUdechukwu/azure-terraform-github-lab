# 02 - Author your resource-group module

[Previous](01-setup.md) | [Course index](../README.md) | [Next](03-network.md)

## Objectives

Create a module's input/resource/output contract, test it without Azure and push
its first commit. A module is ordinary Terraform in its own directory, not a
special resource type.

## 1. Work in the correct repository

```bash
cd "$LAB_HOME/terraform-azurerm-resource-group"
pwd
mkdir -p tests .github/workflows
```

Your current directory must end in `terraform-azurerm-resource-group`, **not**
`course/examples/resource-group-module`.

## 2. Author the provider requirements

Create `versions.tf` using the complete
[reference file](../examples/resource-group-module/versions.tf).
`required_providers` declares the provider source and compatible versions.
`required_version` declares Terraform compatibility. The module does **not**
contain `provider "azurerm"`: the calling root supplies credentials and provider
configuration.

Create `variables.tf` using
[this complete content](../examples/resource-group-module/variables.tf).
Read each field as you type: `type` is the contract, `description` explains it,
and `default = {}` makes tags optional. `name` and `location` have no defaults
because the caller must choose them.

## 3. Author the resource and outputs

Create `main.tf`:

```hcl
resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location
  tags     = var.tags
}
```

`azurerm_resource_group` is the provider's resource type; `this` is a local
Terraform label, not the name Azure sees. `var.name` supplies the Azure name.

Create `outputs.tf` from the complete
[outputs reference](../examples/resource-group-module/outputs.tf).
Expose `name`, `location` and `id`. Exposing resource attributes rather than
merely echoing input variables gives downstream modules a dependency on the
managed resource.

Create `README.md` from the
[module README reference](../examples/resource-group-module/README.md).
Replace `YOUR_GITHUB_USER` with your own username in its usage example. This
README documents what a consumer must supply, what they get back and how to test.

## 4. Write a test that cannot deploy

Create `tests/resource_group.tftest.hcl` from the
[complete mocked test](../examples/resource-group-module/tests/resource_group.tftest.hcl).
`mock_provider "azurerm" {}` replaces Azure API calls. `command = plan` tests the
planned configuration. Assertions check name output and tag propagation.
Mocked tests check module wiring, not Azure quotas, policies or real credentials.
Ordinary Terraform tests can create real resources if they use real providers:
do not remove the mock.

```bash
terraform fmt -recursive
terraform init -backend=false
terraform validate
terraform test
```

Expected: successful initialization/validation and `1 passed, 0 failed`. Downloads
come from the Terraform registry, but no Azure login is needed. A generated
`.terraform.lock.hcl` in this module stays ignored as configured in lesson 01.

**Exercise:** Temporarily change the assertion's expected name to a wrong name.
Run `terraform test`, read the assertion failure, then restore and rerun. This
shows the test can actually catch a regression.

## 5. Add module CI and publish the source commit

Copy [module-ci.yml](../templates/module-ci.yml) into
`.github/workflows/ci.yml`. The working directory is the **repo root**, where
your module files live. No Azure/HCP secrets are needed by these mocked tests.

```bash
git status --short
git add .gitignore README.md versions.tf variables.tf main.tf outputs.tf tests .github
git diff --cached --stat
git diff --cached
git commit -m "Create resource-group module with mocked tests"
git push -u origin main
```

On GitHub, open **Actions** and inspect the passing run. Review your repository
file list: no `.terraform/`, state, tokens or local lock file should be present.
If an ignored file was already tracked, stop and investigate; `.gitignore` does
not remove previously tracked secrets from history.

## Expected result and checkpoint

Your public repo contains the source contract, README and passing mock test.
There is **no release tag yet**. You can describe why this child module should
not decide its consumer's subscription or credentials.

[Previous](01-setup.md) | [Course index](../README.md) | [Next](03-network.md)
