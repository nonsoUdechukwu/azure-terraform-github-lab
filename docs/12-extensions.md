# 12 - Optional extensions and troubleshooting

[Previous](11-scheduled-detection.md) | [Course index](../README.md) | [Next](13-cleanup-capstone.md)

## Objectives

Choose a registry vs Git source deliberately, understand environment isolation,
and diagnose failures without replacing state or granting excessive permissions.

## Extension A: publish to the HCP private module registry

Git releases already publish usable modules. A registry adds a versioned catalog,
discovery and documentation; it is not required for this course. HCP's private
module registry is currently available on Free; verify current account limits.

1. In HCP organization **Registry > Publish > Module**, connect the appropriate
   GitHub VCS provider and select `terraform-azurerm-network`.
2. Confirm repository naming `terraform-azurerm-network` and version tags
   `v1.0.0`/`v1.1.0`. Follow the UI's publication status and module docs.
3. Read the generated usage example. It should resemble:

```hcl
module "network" {
  source  = "app.terraform.io/YOUR_ORG/network/azurerm"
  version = "1.1.0"
  # Keep the same required inputs as your Git-source module call.
}
```

Use the **exact source from your registry UI**, not a guessed namespace.
Unlike Git sources, registry sources use `version`, not `?ref=`.
Make the source change in a live feature branch, retain the same module block
name, run init/validate, review the PR's plan and confirm no resource changes
before merging.

HCP-hosted runs in the same organization can use their registry integration.
Local private-registry init may require `terraform login app.terraform.io`;
do not commit the generated credentials file. GitHub CI does **not** inherit
your local/HCP credentials. Either provision appropriately scoped registry
access via repository secrets and a reviewed workflow, or keep the public
Git-source CI baseline for this beginner course. The provided live CI template
is intentionally credential-free and must be adapted before this extension.

The GitHub App being able to fetch a live private repository does not
automatically authenticate arbitrary private Git source URLs. Do not embed a
token in a Git source string. Prefer the registry's documented authentication
or explicitly configured private module access.

## Extension B: a separate second environment

Do this only if you have time/budget and have completed cleanup once.

1. On a new live feature branch, copy `environments/dev` to
   `environments/test`, excluding `.terraform/`, state and plans. Preserve the
   reviewed provider lock file.
2. Change Azure names to include `test`, the `environment` tag to `test`, and
   use a separate suffix/address range (for example `10.43.0.0/16` with
   `10.43.1.0/24` and `10.43.2.0/24`). Change the actual name expressions in
   `main.tf`, not just the tag. Add a precise ignore exception only for this
   reviewed non-secret `environments/test/terraform.tfvars`.
3. Create a separate HCP workspace `azure-platform-test`, directory
   `environments/test`, remote mode, manual apply, same Terraform baseline.
   Never point two workspaces at the same intended Azure resource names.
4. Create two new federated subjects for that workspace. Prefer a separate
   application/service principal and scoped permissions for stronger isolation;
   update HCP environment variables to that identity. Never reuse dev state.
5. Extend CI with a directory matrix for dev/test so both are validated.
   Review independent plans and destroy **both** environments when done.

HCP workspaces isolate state and variables; an HCP project name alone does not.
This lab uses directory-based environments, not Terraform CLI workspaces.

## Troubleshooting: read the earliest meaningful error

| Symptom | Check and safe action |
|---|---|
| Terraform version constraint failure | Install/select 1.15.3 locally and in HCP/CI; do not casually loosen the baseline |
| `Module not installed` after source edit | Run local `init -backend=false`; inspect exact Git ref and remote tag |
| Git clone 404/private module failure | Replace username placeholder; verify public visibility/tag; registry/private clone auth is separate |
| `version` invalid with Git source | Remove `version`; pin Git with `?ref=v1.0.0` |
| AzureRM checksum mismatch on Linux | Generate multi-platform lock hashes from registry; commit lock; investigate mirrors before regenerating |
| OIDC no matching federated identity | Exact HCP org/project/workspace/case, issuer without slash, correct audience and plan/apply phase |
| Plan works, apply authentication fails | Missing apply-phase credential or different apply identity settings |
| Native auth conflict | Remove manually set `ARM_CLIENT_ID`, `ARM_USE_OIDC`, `ARM_OIDC_TOKEN` and client secrets, including inherited variable sets |
| Authorization failed | Verify service-principal object ID, role scope, selected subscription and propagation delay |
| Cannot create app / assign role | Entra app rights and Azure RBAC assignment rights are separate; ask authorized admin |
| Resource provider not registered | Human registers `Microsoft.Network`; keep root registration setting intentional |
| Region/policy/address error | Inspect allowed regions, naming/tag policies and subnet CIDRs; adjust desired code through PR |
| Wrong directory / no Terraform files | HCP and live CI must use `environments/dev`; module CI uses repo root |
| Unexpected resource deletion/replacement | Stop; compare state addresses, map keys and module diffs; do not approve blindly |
| Workspace locked/queued | Inspect current run/owner; wait or cancel that run appropriately; never force-unlock an active writer |
| No drift detected | Confirm right subscription/VNet, refreshed plan, latest config, no tag ignore rule, no prior repair |
| Refresh-only didn't repair Azure | Expected: it changes state, not desired configuration or Azure; use a normal reviewed apply |
| Scheduler red | Read message: exit 2 means changes; exit 1 means failure; inspect HCP run before retry |
| No scheduled Actions run | Workflow must be on default branch, enabled, token valid; cron is UTC and can be delayed/disabled for inactivity |
| Azure object exists but state is empty | Stop; identify original workspace/state. Do not duplicate or import blindly; agree ownership with instructor |
| Secret accidentally committed | Revoke/rotate first, notify owner, then follow GitHub sensitive-data removal guidance; deleting latest file is insufficient |

Never solve these errors by deleting state, retagging published code, suppressing
tag differences, or running a second local apply against the same objects.

## Expected result, checkpoint and exercise

Pick two plausible errors and describe the minimum evidence needed to diagnose
them without sharing tokens, state or account IDs in public. Extensions are
optional; completing the core course does not require either.

[Previous](11-scheduled-detection.md) | [Course index](../README.md) | [Next](13-cleanup-capstone.md)
