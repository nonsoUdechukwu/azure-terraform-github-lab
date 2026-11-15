# 08 - Deploy, inspect state and practice pull requests

[Previous](07-azure-oidc.md) | [Course index](../README.md) | [Next](09-upgrade.md)

## Objectives

Approve the first real deployment through HCP, verify the result in Azure, then
practice the difference between a PR preview and a post-merge apply.

## 1. Queue a normal run

In HCP `azure-platform-dev`, choose **New run > Plan and apply**.
Auto-apply must still be disabled. Add a message such as `Initial dev deployment`.
If an earlier credentials-free run failed, create a fresh run using the current
configuration rather than approving an old/stale plan.

Inspect initialization logs: working directory `environments/dev`, Terraform
1.15.3, AzureRM 4.50.0, both module Git refs v1.0.0. Provider authentication
must use the dynamic credentials; no local `az login` session is available on
the HCP worker.

## 2. Review the initial plan before confirming

Expected addresses:

```text
+ module.resource_group.azurerm_resource_group.this
+ module.network.azurerm_virtual_network.this
+ module.network.azurerm_subnet.this["app"]
+ module.network.azurerm_subnet.this["data"]
Plan: 4 to add, 0 to change, 0 to destroy.
```

Root outputs are also added; those are not additional managed Azure resources.
Check names, location, tags, VNet `/16`, subnet `/24`s, and disabled implicit
default outbound. If you see replacement/destruction or more resources, stop
and compare your configuration with lesson 05.

Confirm apply manually only when the plan is understood. If it fails, do not
recreate resources by hand to hide the failure. Inspect logs/state, fix the
cause and queue another run. Partial success is tracked in state where possible.

## 3. Verify Azure and HCP independently

Expected: HCP apply completes, state lists four resource instances, outputs
include your RG name and subnet ID map. In Azure Portal, open the exact RG and
VNet; the VNet's **Subnets** page should list app and data subnets. Subnets may
not appear as separate top-level resource-group rows.

Read-only terminal verification, using the same training subscription:

```bash
az network vnet show \
  --resource-group rg-tflab-dev-learner01 \
  --name vnet-tflab-dev-learner01 \
  --query "{name:name,addressSpace:addressSpace.addressPrefixes,tags:tags}" -o json
az network vnet subnet list \
  --resource-group rg-tflab-dev-learner01 \
  --vnet-name vnet-tflab-dev-learner01 \
  --query "[].{name:name,prefix:addressPrefix,prefixes:addressPrefixes}" -o table
```

Substitute your actual suffix if changed. Do not publish raw ID-bearing outputs.
Run **New run > Plan only** in HCP; expected no configuration changes after a
successful baseline apply. This is a point-in-time check, not monitoring.

## 4. Make a reviewed change in the live repository

```bash
cd "$LAB_HOME/azure-platform-live"
git switch main
git pull --ff-only
git switch -c update-cost-center
```

In `environments/dev/main.tf`, change only
`cost_center = "training"` to `cost_center = "training-reviewed"`.

```bash
terraform -chdir=environments/dev fmt
terraform -chdir=environments/dev validate
git add environments/dev/main.tf
git diff --cached
git commit -m "Update training cost-center tag"
git push -u origin update-cost-center
gh pr create --base main --title "Update training cost-center tag" \
  --body "Change cost_center on the RG and VNet. Expect two in-place updates, no replacements."
```

Open the PR. Review CI and the HCP speculative plan. Expect **0 add, 2 change,
0 destroy**: RG and VNet tags only. No subnet changes because subnets lack tags.
Have your instructor/partner review, then merge through GitHub. If working
alone, record your review reasoning in the PR before merging; do not claim a
self-reviewed PR is an independent approval.

HCP queues a **new** default-branch plan. Review this plan again and manually
approve apply. The speculative plan itself is not reused or directly applied.
Afterward:

```bash
git switch main
git pull --ff-only
```

## Expected result and checkpoint

Four resources exist; the two tagged parent resources have the reviewed
cost-center value. A subsequent plan-only check is empty. Your PR records what
changed and why.

**Exercise:** Describe where state is stored and why a successful laptop
`terraform validate` cannot prove Azure RBAC, regional quota or subscription
policy compliance.

[Previous](07-azure-oidc.md) | [Course index](../README.md) | [Next](09-upgrade.md)
