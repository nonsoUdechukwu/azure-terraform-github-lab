# 00 - Orientation, safety and glossary

[Course index](../README.md) | [Next: setup](01-setup.md)

## Objectives

Explain which system owns code, credentials, execution and state. Know what
you will create before granting access or spending money.

## 1. Draw the ownership boundary

GitHub stores configuration and module releases. HCP Terraform checks out the
live repository, downloads the pinned modules, runs Terraform on remote
workers, and stores state. Azure accepts a short-lived HCP-issued OIDC identity
and creates resources. Your laptop writes code and runs mocked tests.

There are **two different kinds of tags**:

| Term | Example | Meaning |
|---|---|---|
| Git release tag | `v1.0.0` | A Git reference to a module source commit |
| Azure resource tag | `environment = "dev"` | Metadata on an Azure resource |

Changing an Azure tag does not publish module code. Publishing a Git tag does
not deploy anything until a consumer chooses it and applies a plan.

## 2. Confirm costs and permissions

Use your own training subscription with no production resources. Inspect
[Azure network pricing](https://azure.microsoft.com/en-us/pricing/details/virtual-network/).
This lab creates only an empty RG, VNet and two subnets; it does not create
billable network appliances. Do not attach paid services during the course.
Set a budget and billing alerts in Azure Cost Management before deploying;
these **do not stop spending**. Quotas, policies and regional restrictions can
still prevent deployment.

HCP Terraform Free currently permits up to 500 managed resources org-wide,
not per workspace. This lab initially uses four. Check your current plan:
[HCP overview](https://developer.hashicorp.com/terraform/cloud-docs/overview).
Free has limited concurrent remote execution. This course does not require
paid health assessments, policy products or paid GitHub features.

You need a GitHub account, an HCP Terraform account/organization, an Azure
subscription, and permission to create Entra apps and Azure role assignments.
Azure subscription Contributor alone does **not** grant role-assignment or
Entra application-creation permission. Have an authorized administrator perform
lesson 07 if necessary.

## 3. Adopt these safety rules

1. Never commit credentials, HCP tokens, state files, saved plans or `.terraform/`.
   State and plans can contain sensitive data even when outputs say `sensitive`.
2. Do not run local `terraform apply`, `destroy`, `import` or state commands for
   this live environment. HCP owns its state. This course deliberately has no
   local backend connection.
3. Keep HCP auto-apply off; inspect every non-speculative plan before approving.
4. Do not modify or retag published module versions. Release a new version.
5. Public repository examples must use dummy owner labels, not personal emails,
   tokens, subscription IDs or exported Azure CLI responses.
6. Follow lesson 13 before removing HCP/Azure access. Keep the identity working
   until Terraform has destroyed its resources.

## 4. Learn the working vocabulary

| Word | Meaning in this lab |
|---|---|
| Root module | `azure-platform-live/environments/dev`; the entrypoint Terraform executes |
| Child module | Reusable resource-group/network code called by the root |
| Provider | Plugin that speaks Azure's API; AzureRM in this course |
| Input/output | A module's public contract; pass values in, expose selected values out |
| State | Terraform's binding between resource addresses and remote objects |
| Plan | Proposed actions based on configuration, state and refreshed remote data |
| Apply | Execution of an approved plan and persistence of resulting state |
| Drift | A managed remote object differs from the configuration/state expectations |
| Speculative plan | Preview for a PR; cannot be used as the later approved apply plan |
| Workspace | HCP execution settings, variables, run history and one state boundary |
| Working directory | Folder inside a checkout where Terraform starts |
| OIDC federation | Azure trusts specific short-lived HCP identity claims |
| Service principal | Tenant-local identity that receives Azure RBAC permissions |
| Semantic versioning | Major: breaking; minor: compatible addition; patch: compatible fix |
| Lock file | Provider versions/checksums; **not** remote module versions |

## Expected result and checkpoint

You can explain why a public GitHub repository does not imply public HCP state,
why Terraform cannot generally discover every unmanaged Azure object, and why
you must not delete the deployment identity first.

**Exercise:** Name the four initial resources. Which are Azure-tagged?
Answer before continuing: RG and VNet support tags; subnets do not.

[Course index](../README.md) | [Next: setup](01-setup.md)
