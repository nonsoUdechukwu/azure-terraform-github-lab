# Azure + Terraform + GitHub: publish, deploy, detect change

A hands-on course for someone who has just learned Terraform syntax. You will
write two reusable modules, publish versioned releases in **your own GitHub
repositories**, consume them from a third repository, and deploy a small network
through HCP Terraform using short-lived Azure credentials.

Allow 6-10 hours across several sessions. Use a dedicated training subscription,
not a production subscription. You need permission to create Entra applications
and assign Azure roles; ask your administrator before starting.

## What you build

```text
Your GitHub account
  terraform-azurerm-resource-group -- v1.0.0 -------+
  terraform-azurerm-network ------ v1.0.0/v1.1.0 --+--> azure-platform-live
                                                       environments/dev
                                                              |
                                                       HCP Terraform
                                                    plan -> review -> apply
                                                              |
                                                Azure (OIDC, no client secret)
                                                resource group
                                                  virtual network
                                                    app + data subnets
```

The initial deployment has **four managed resources**: one resource group, one
VNet and two standalone subnets. No VM, gateway, public IP, NAT or firewall is
needed. Resource groups and empty VNets/subnets have no base network charge,
but paid attachments and traffic can cost money. Budgets are alerts, not hard
spending caps. Always complete the destroy lesson.

## Start here: follow the lessons in order

| Lesson | Result |
|---|---|
| [00 - Orientation, safety and glossary](docs/00-orientation.md) | Understand the systems and costs |
| [01 - Tools and your three repositories](docs/01-setup.md) | Independent local clones and GitHub repos |
| [02 - Author the resource-group module](docs/02-resource-group.md) | Inputs, resource, outputs, mocked test |
| [03 - Author the network module](docs/03-network.md) | VNet, subnet map and module composition |
| [04 - Publish immutable module releases](docs/04-publish.md) | Annotated tags and GitHub Releases |
| [05 - Build the live configuration](docs/05-live.md) | Git-pinned sources and provider lock file |
| [06 - Configure HCP Terraform Free](docs/06-hcp.md) | VCS workspace, remote execution and state |
| [07 - Connect Azure with OIDC](docs/07-azure-oidc.md) | Two trust credentials, no stored Azure password |
| [08 - Deploy and use pull requests](docs/08-deploy.md) | Reviewed plans and manually approved applies |
| [09 - Release and adopt v1.1.0](docs/09-upgrade.md) | Deliberate module upgrade |
| [10 - Detect, reject and adopt drift](docs/10-drift.md) | Evidence-based reconciliation |
| [11 - Optional scheduled change detection](docs/11-scheduled-detection.md) | Bounded, plan-only API automation |
| [12 - Extensions and troubleshooting](docs/12-extensions.md) | Registry, second environment, common fixes |
| [13 - Destroy and demonstrate learning](docs/13-cleanup-capstone.md) | Cleanup, capstone and instructor rubric |

## How to use this repository

Clone this course to read and copy files. **Do not deploy the bundled examples
directly.** They are reference snapshots, not your three learner repositories.
Lessons say exactly where each file goes and when to commit, push and tag.
Commands use a POSIX shell (macOS, Linux or WSL) unless stated otherwise.

| Directory | Purpose |
|---|---|
| [`examples/resource-group-module`](examples/resource-group-module) | Resource-group v1.0.0 source and mocked tests |
| [`examples/network-module`](examples/network-module) | Network v1.0.0 source and mocked tests |
| [`examples/network-module-v1.1.0`](examples/network-module-v1.1.0) | Only the added v1.1.0 output and its test |
| [`examples/live/environments/dev`](examples/live/environments/dev) | Live configuration; replace `YOUR_GITHUB_USER` |
| [`templates`](templates) | Copyable learner CI and optional scheduler; not enabled here |
| [`scripts`](scripts) | Offline course validation, no deployments |

Terraform **1.15.3** and AzureRM **4.50.0** are the reproducible teaching
baseline, not a claim that either is the newest release. Modules accept AzureRM
`>= 4.50.0, < 5.0.0`; the live root pins it exactly. Do not mix provider-major
upgrades into these exercises.

HCP Terraform Free currently supports up to **500 managed resources in total
across the organization**, subject to its current terms and concurrency limits.
Built-in scheduled Health Assessments/drift monitoring require Standard or
Premium; they are **not included in this Free lab**. Manual refreshing plans
work here. The optional scheduler detects changes, not exclusively drift.

## Course validation

Maintainers run `bash scripts/validate.sh` (Terraform, Python 3.9+, Ruby and network access
for provider installation required). GitHub Actions runs the same command:
formatting, initialization without a backend, validation, mocked tests, and
local Markdown link checks. It never authenticates to Azure or runs a real
plan/apply. The course live root is validated with temporary local module
sources; learner Git source URLs are checked separately.

No live Azure deployment is represented by these offline checks. Learners
verify that separately in lessons 08 and 13.

## Primary references

- [HCP Terraform overview and current plans](https://developer.hashicorp.com/terraform/cloud-docs/overview)
- [Health Assessments availability](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/health)
- [Azure dynamic provider credentials](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/azure-configuration)
- [Azure virtual network pricing](https://azure.microsoft.com/en-us/pricing/details/virtual-network/)
- [Terraform 1.15.3 distribution](https://releases.hashicorp.com/terraform/1.15.3/)
