# 05 - Build the live configuration

[Previous](04-publish.md) | [Course index](../README.md) | [Next](06-hcp.md)

## Objectives

Compose your released modules, choose inputs, lock provider packages and push
the environment configuration without deploying from your laptop.

## 1. Create the environment root

```bash
cd "$LAB_HOME/azure-platform-live"
mkdir -p environments/dev .github/workflows
cp "$COURSE"/examples/live/environments/dev/*.tf environments/dev/
cp "$COURSE/examples/live/environments/dev/terraform.tfvars" environments/dev/
cp "$COURSE/templates/live-ci.yml" .github/workflows/ci.yml
```

Read each reference while editing your own copy:

| File | Meaning |
|---|---|
| [versions.tf](../examples/live/environments/dev/versions.tf) | Exact Terraform 1.15.3 and AzureRM 4.50.0 baseline |
| [providers.tf](../examples/live/environments/dev/providers.tf) | Provider configuration; registration disabled deliberately |
| [variables.tf](../examples/live/environments/dev/variables.tf) | Region, unique learner suffix, VNet purpose |
| [main.tf](../examples/live/environments/dev/main.tf) | Two pinned Git modules, dataflow and resource tags |
| [outputs.tf](../examples/live/environments/dev/outputs.tf) | Root-visible results |
| [terraform.tfvars](../examples/live/environments/dev/terraform.tfvars) | Reviewed, non-sensitive dev values |

In `environments/dev/main.tf`, replace **both** `YOUR_GITHUB_USER` occurrences
with your GitHub username. Keep `?ref=v1.0.0` on each source. Example:

```hcl
source = "git::https://github.com/YOUR_GITHUB_USER/terraform-azurerm-network.git?ref=v1.0.0"
```

This is a Git source, so **do not** add `version = "1.0.0"`. That argument
belongs to registry sources. Terraform requires module sources to be literal
strings, not variables.

## 2. Follow the dependency and tagging decisions

`module.network.resource_group_name` receives `module.resource_group.name`.
The reference to an actual resource output supplies ordering automatically.
Do not add a blanket module `depends_on`; it can make plans less precise.

`common_tags` includes `project`, `environment`, dummy `owner`, `cost_center`
and `managed_by`. The VNet additionally receives
`purpose = var.vnet_purpose`. This VNet-only tag makes drift changes unambiguous
later. Use `learner-demo`, not your personal email, for public owner metadata.

Edit `terraform.tfvars`: choose an allowed region and a unique suffix such as
`learner01`. Leave `vnet_purpose = "training"`. Baseline names are
`rg-tflab-dev-learner01` and `vnet-tflab-dev-learner01`.
Do not put Azure credentials or identifiers in this public file.

## 3. Initialize for validation only and generate a portable lock

```bash
cd "$LAB_HOME/azure-platform-live/environments/dev"
terraform fmt
terraform init -backend=false
terraform providers lock -platform=linux_amd64 -platform=darwin_arm64 -platform=darwin_amd64 -platform=windows_amd64
terraform validate
```

`init` should download your two v1.0.0 Git modules and AzureRM 4.50.0.
The lock command includes the Linux remote-worker package and common learner
platforms. The resulting `.terraform.lock.hcl` locks provider selections and
checksums; it **does not lock modules**. Their Git refs do that.

There is deliberately no `backend` or `cloud` block. In a VCS-connected HCP
workspace, remote execution/state are configured in HCP. Locally this root is
**not connected to that state**. Run only formatting/init/validate here, not
local `plan`, `apply`, `destroy`, `import` or state operations. `-backend=false`
is not itself a guard against later local applies.

Provider registration is disabled in `providers.tf` to avoid giving every run
subscription-level registration work. An authorized human registers
`Microsoft.Network` in lesson 07.

## 4. Add a live README and push

Create your live repository's `README.md` describing: purpose, working directory
`environments/dev`, HCP workspace name `azure-platform-dev`, manual apply
requirement, and the rule that local commands do not deploy.
Do not include account IDs or state exports.

```bash
cd "$LAB_HOME/azure-platform-live"
git check-ignore environments/dev/terraform.tfvars || true
git status --short
git add .gitignore README.md .github environments/dev/*.tf \
  environments/dev/terraform.tfvars environments/dev/.terraform.lock.hcl
git diff --cached
git commit -m "Compose released modules for dev"
git push -u origin main
```

`git check-ignore` should produce no output: lesson 01 explicitly allowed this
one non-secret file. Check staged content before committing. The `.terraform/`
directory must remain ignored. CI runs in `environments/dev`, not repo root.

## Expected result and checkpoint

Your live repo resolves your own release tags and passes init/validate. No
Azure resources exist yet. The initial future plan will be four additions.

**Exercise:** Why won't editing a file in your local module repo change an
already tagged remote module used by HCP? Trace the download from source URL
to tag to commit.

[Previous](04-publish.md) | [Course index](../README.md) | [Next](06-hcp.md)
