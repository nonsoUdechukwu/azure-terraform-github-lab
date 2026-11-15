# 06 - Configure HCP Terraform Free

[Previous](05-live.md) | [Course index](../README.md) | [Next](07-azure-oidc.md)

## Objectives

Connect your live repository to a VCS-driven HCP workspace, configure the correct
directory and understand which features the Free plan actually provides.

## 1. Create the organization and project

Sign in at [HCP Terraform](https://app.terraform.io). Create or choose your
training organization. Record its exact organization name privately as `HCP_ORG`;
the URL slug, spelling and case must match the identity trust in lesson 07.
Choose the Free plan if the UI offers a plan choice. Review your account's
current resource/concurrency limits and any trial expiration.

Create a **project** called exactly `Terraform-Labs`. The project is an HCP
grouping of workspaces, not an Azure resource group or GitHub Project.

## 2. Connect GitHub and create the workspace

Choose **New workspace > Version control workflow > GitHub** and follow the
GitHub App authorization/installation flow. Grant repository access only to
your `azure-platform-live` repository where possible. If GitHub requires an
organization administrator's approval, obtain it rather than broadening access.

Select your live repository and configure:

| Setting | Value |
|---|---|
| Workspace name | `azure-platform-dev` |
| Project | `Terraform-Labs` |
| VCS branch | `main` |
| Terraform working directory | `environments/dev` |
| Execution mode | Remote |
| Terraform version | `1.15.3` (not `latest`) |
| Auto-apply | Off; require manual approval |
| PR/speculative plans | Enabled |

UI labels can move; verify these effective settings after creation.
Do not configure the course repository or either module repo as this workspace's
VCS source. A default-branch module commit alone must not deploy this workspace.

If configuring path filters, include `environments/dev/**`. For this small repo,
leaving filters at defaults is safer than an incorrect filter that skips runs.
An initial run may be queued before Azure credentials exist; let it fail or
discard it. Do not approve any apply. Configure trust before retrying.

## 3. Understand variables and state

The committed dev `terraform.tfvars` supplies non-sensitive Terraform inputs.
No duplicate HCP Terraform variables are needed for them. If you later add
workspace Terraform variables, check
[variable precedence](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/variables)
rather than assuming edits to a file always win.

Lesson 07 adds **environment variables** for provider authentication; these
are a different UI category from Terraform input variables. Never add a
long-lived Azure client secret.

HCP stores state for this workspace and serializes state-changing runs.
Review organization/workspace membership; do not make state public or enable
unnecessary cross-workspace state sharing. Logs, state and outputs may contain
subscription/resource identifiers. Do not copy them into public issues.

## 4. Separate the three HCP run modes

| UI choice | Effect |
|---|---|
| Plan only | Review proposed changes; cannot apply that run |
| Plan and apply | Plan now; human confirms apply when auto-apply is off |
| Refresh state | Refresh-only mode; review/persist state updates, no normal infrastructure reconciliation |

A PR preview is speculative. Merging creates a **new non-speculative run**;
you must review that new plan, not assume the PR's plan will be reused.
See [run modes](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/modes-and-options).

## 5. Check Free vs paid drift features

Built-in scheduled **Health Assessments** and their drift/continuous-validation
features require Standard/Premium. They are not a Free-tier prerequisite.
This lab teaches manually initiated refreshing plans and an optional external,
plan-only scheduler. Neither turns Free into the paid health-assessment product.
See [feature availability](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/health)
and [GitHub App setup](https://developer.hashicorp.com/terraform/cloud-docs/vcs/github-app).

## Expected result and checkpoint

You can locate the workspace's settings, variables, runs and state pages.
Confirm the exact org/project/workspace names before building OIDC trust.
No successful deployment is expected yet.

**Exercise:** Explain why the GitHub App's ability to fetch the live repo does
not automatically grant arbitrary private Git module clone access. Public
module Git URLs avoid that separate authentication problem in this lab.

[Previous](05-live.md) | [Course index](../README.md) | [Next](07-azure-oidc.md)
