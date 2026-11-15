# 13 - Destroy safely and demonstrate learning

[Previous](12-extensions.md) | [Course index](../README.md) | End

## Objectives

Remove all lab resources while the deployment identity still works, revoke
unneeded access, and demonstrate independent understanding with a small capstone.

## 1. Stop automation before destroying

If you enabled lesson 11, disable the scheduled workflow in GitHub or remove
its schedule through a reviewed change. Check pending GitHub jobs and HCP runs.
Cancel/discard obsolete specific runs before queuing the destroy.
Do not revoke the Azure identity's permissions yet.

If you built test or other environments, inventory every HCP workspace and
subscription/resource group involved. Each state must be destroyed separately.

## 2. Review and execute HCP destroy

Open the **correct HCP workspace**, confirm directory/branch/subscription and
review the latest state. In workspace **Settings > Destruction and Deletion**
(or the current UI's **Queue destroy plan** action), unlock destruction only
if required by the workspace's protection setting. Queue a **destroy run**.
This is different from deleting a workspace record.

Expected baseline: **0 add, 0 change, 4 destroy**. Review all four addresses:
two subnets, VNet and RG. Stop if unexpected resources are listed. Confirm the
destroy manually. Keep OIDC credentials and RBAC intact until it succeeds.

The provider may refuse RG deletion if untracked resources were added. Inspect
those resources with your instructor. Do not disable safety checks to force
deletion of someone else's resource. Remove only resources you own through
their correct management process.

## 3. Verify absence and empty state

HCP destroy must finish successfully and state should contain no managed lab
resources. In Azure:

```bash
az group exists --name rg-tflab-dev-learner01
```

Expected: `false` in the same training subscription; use your chosen suffix.
Check the portal, too. If you have other lab environments, repeat for each.
Review Azure Cost Management for unexpected paid attachments; cost reporting
can lag and deleting resources does not erase previously incurred charges.

Do not queue another normal apply afterward: the configuration still describes
the network and would recreate it.

## 4. Clean up identities, tokens and integrations

Only after all destroys and state checks succeed:

1. Revoke the optional HCP **user API token** in HCP, remove GitHub secret
   `HCP_TERRAFORM_TOKEN` and variable `HCP_WORKSPACE_ID`, and ensure the scheduler
   remains disabled/removed.
2. As the authorized bootstrap administrator, remove the **specific lab role
   assignment** using its privately recorded ID, e.g.
   `az role assignment delete --ids "YOUR_LAB_ROLE_ASSIGNMENT_ID"`.
   Do not delete all assignments for an account/subscription.
3. In Entra, delete only the lab federated credentials, service principal
   (Enterprise application) and app registration. Inspect their recorded
   object/client IDs first. If you prefer CLI after verifying them:
   `az ad sp delete --id "$SP_OBJECT_ID"` and
   `az ad app delete --id "$APP_OBJECT_ID"`. App deletion removes its federated
   credentials; do not delete any shared identity.
4. Remove HCP workspace environment variables and delete/archive the empty
   workspace if appropriate. Preserve run evidence privately if required;
   state-history handling should follow your organization's retention policy.
5. Remove the GitHub App's repository access only if no remaining workspace
   needs it. Keep public module release repositories as your portfolio, or
   archive them deliberately. Never commit exported state as evidence.

No `az logout` command removes Azure identities or deployed resources; it only
clears your local CLI session. Provider registration can normally remain on the
training subscription; do not unregister a namespace other users may need.

## Capstone: run this before final destroy, or rebuild deliberately

After completing the guided path, repeat a small change without copying the
answer. If you've already destroyed, consciously approve the four-resource
rebuild before starting, then destroy again afterward.

1. Publish network **v1.2.0** with an additive `subnet_prefixes` output mapping
   stable keys to configured prefix lists. Add one meaningful mocked assertion
   and release notes; preserve v1.0.0/v1.1.0 unchanged.
2. Upgrade the live consumer in a PR, exposing the new output. Predict the
   plan before opening HCP. Explain why no Azure writes are intended.
3. Change only the VNet purpose tag manually. Capture a private plan excerpt
   with identifiers removed. Demonstrate rejection **or** adoption and justify
   your choice. State what a refresh-only apply would and would not do.
4. Destroy all managed lab resources and show absence plus empty state without
   posting credentials or raw state.

## Instructor answers and rubric

| Evidence | Points | Expected reasoning |
|---|---:|---|
| Independent module repos with inputs/outputs/tests | 20 | Child declares requirements, caller configures provider; tests mock Azure |
| Immutable annotated releases and notes | 15 | Tags reference code, Azure tags label resources; no moved old refs |
| Live pinned consumer and portable provider lock | 15 | Git `ref` vs registry `version`; lock file does not lock modules |
| HCP/OIDC and reviewed first deployment | 15 | HCP issuer, two exact phase subjects, four resources, no client secret |
| PR output-only module upgrade | 10 | New release does not update consumers automatically; output state can change without Azure writes |
| Drift detection/reconciliation explanation | 15 | Normal refresh sees managed-resource changes; refresh-only updates state, not config/infrastructure |
| Safe destroy and credential cleanup | 10 | Destroy before revocation, every environment checked, no leaked evidence |

Suggested pass: 80/100 **and** no skipped safety requirements. A passing score
cannot compensate for leaking a token, destroying another user's resources or
leaving resources/identities active unintentionally.

Expected guided checkpoints: initial plan `4 add`; cost-center PR `2 change`;
v1.1.0 upgrade `0` resource changes plus output; drift rejection `1 change`;
adoption no resource write when code already matches portal; destroy `4 destroy`.
Provider refresh messages may vary; grade the intended actions and explanation,
not exact terminal punctuation.

The capstone output can be implemented with
`{ for key, subnet in azurerm_subnet.this : key => subnet.address_prefixes }`.
Test the app/data values as lists. A compatible new output is a minor release,
not a reason to rewrite v1.0.0.

## Expected result and final checkpoint

You have published reusable modules, deployed through reviewed remote runs,
reconciled drift and removed the infrastructure. You can teach the lifecycle
again without confusing Git release tags, Azure resource tags, provider locks,
module refs, speculative plans or refresh-only state updates.

[Previous](12-extensions.md) | [Course index](../README.md) | End
