# 10 - Detect, reject and adopt drift

[Previous](09-upgrade.md) | [Course index](../README.md) | [Next](11-scheduled-detection.md)

## Objectives

Create one safe, reversible out-of-band change, inspect what a refreshing plan
detects, and choose whether configuration or the manual change should win.

## 1. Establish a clean baseline

Finish all earlier applies. Confirm no unapplied code/variable changes or
pending runs. In HCP queue **Plan only**; expected no changes.
The live configuration still says `vnet_purpose = "training"`.

Three different things now agree: desired configuration, recorded state and
the actual VNet's purpose tag. Record the baseline commit and HCP run privately.

## 2. Introduce drift deliberately

In Azure Portal, open **only the lab VNet > Tags**. Change only `purpose` from
`training` to `changed-in-portal` and save. Leave the resource group's tags,
names, address ranges and subnet configuration alone.

This is the sole deliberate infrastructure edit outside Terraform in the
exercise. Do not use a command that overwrites the entire tags map. Do not
experiment with deletion or production resources.

## 3. Detect it with a normal refreshing plan

In HCP queue **Plan only**, with refresh enabled (the default).
Inspect both the "changed outside Terraform" information, if shown, and the
proposed reconciliation. Expected: VNet purpose tag would change
`changed-in-portal -> training`, **0 add, 1 change, 0 destroy**.
Provider formatting of the plan may vary; the decisive evidence is the tag diff.

This run does **not** repair Azure. Visit the VNet again: the portal value
remains `changed-in-portal`. A normal plan refreshes its working view of remote
objects; a plan-only preview does not by itself persist a reconciled state
snapshot or change the configuration.

Normal refreshing plans compare configuration against managed remote objects.
They can also include changes caused by new code/variables/provider behavior.
Not every non-empty plan is exclusively drift. Terraform also cannot generally
detect unmanaged resources that were never in its state. This is not a
subscription-wide inventory/security scanner.

## 4. Reject drift: make code win

Choose **New run > Plan and apply**. The earlier plan-only run cannot be applied.
Review the new plan: one VNet in-place tag update, no replacements.
Approve it manually. Verify Azure purpose is back to `training`, then run
another plan-only check; expected no changes.

Do not add `ignore_changes = [tags]` to hide the difference. That would abandon
the tag management behavior you are learning to reconcile.

## 5. Adopt drift: make a reviewed configuration change

Repeat the portal edit, setting VNet `purpose = "changed-in-portal"` again.
Now decide this value is desired. In your live repo:

```bash
cd "$LAB_HOME/azure-platform-live"
git switch main
git pull --ff-only
git switch -c adopt-vnet-purpose
```

Edit `environments/dev/terraform.tfvars` to
`vnet_purpose = "changed-in-portal"`. Do not change the provider's state or tags
with ignore rules.

```bash
terraform -chdir=environments/dev fmt
terraform -chdir=environments/dev validate
git add environments/dev/terraform.tfvars
git diff --cached
git commit -m "Adopt reviewed VNet purpose value"
git push -u origin adopt-vnet-purpose
gh pr create --base main --title "Adopt VNet purpose tag" \
  --body "Approve the intentional portal change in desired configuration. Azure already matches; expect no infrastructure action after refresh."
```

Review the speculative plan and merge the PR. Then review the new normal run.
Because Azure already matches the new desired configuration, expect no VNet
write, although external-change/state/output messages may appear.
Persist refreshed state if needed using a reviewed **Refresh state** run; do
not assume a no-op preview wrote state. Queue a final normal plan-only run to
confirm configuration and refreshed remote data now agree.

## 6. Understand refresh-only without confusing it with adoption

| Operation | Changes configuration files? | Changes Azure resources? | Can persist refreshed state? |
|---|---|---|---|
| Normal plan-only | No | No | Not by itself |
| Normal reviewed apply | No | Yes, if proposed | Yes |
| Refresh-only plan | No | No | Not until its reviewed apply |
| Reviewed refresh-only apply | No | No | Yes |
| Edit/merge configuration PR | Yes | Not by itself | Not by itself |

HCP's **Refresh state** mode is refresh-only; inspect/confirm its state
changes. If you had persisted portal tag drift with refresh-only while leaving
configuration at `training`, the next **normal** plan would still propose
returning Azure to `training`. Refresh-only does not adopt a change into code
and is not a repair operation.

## Expected result and checkpoint

You have demonstrated both outcomes: rejected drift restored by normal apply,
then adopted drift codified through a PR. The final normal plan has no changes.

**Exercise:** Explain why running `plan -refresh=false` would weaken this drift
exercise, and why paid scheduled Health Assessments are not the same thing as
a single refreshing plan on Free.

[Previous](09-upgrade.md) | [Course index](../README.md) | [Next](11-scheduled-detection.md)
