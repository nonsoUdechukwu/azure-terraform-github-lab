# 09 - Publish and deliberately adopt network v1.1.0

[Previous](08-deploy.md) | [Course index](../README.md) | [Next](10-drift.md)

## Objectives

Extend a module compatibly, release it without rewriting v1.0.0, and upgrade
only the consumer that chooses the new ref.

## 1. Add an output on a module feature branch

```bash
cd "$LAB_HOME/terraform-azurerm-network"
git switch main
git pull --ff-only
git switch -c add-subnet-names
cp "$COURSE/examples/network-module-v1.1.0/outputs-addition.tf" .
cp "$COURSE/examples/network-module-v1.1.0/upgrade.tftest.hcl" tests/
```

Read the [new output](../examples/network-module-v1.1.0/outputs-addition.tf)
and [test](../examples/network-module-v1.1.0/upgrade.tftest.hcl).
`subnet_names` preserves caller map keys while exposing Azure names. It adds
an interface; it does not rename any resources or change the v1.0.0 outputs.
Update your module README title to v1.1.0, add this output and note that
existing callers remain compatible. Keep the existing resources/tests.

```bash
terraform fmt -recursive
terraform init -backend=false
terraform validate
terraform test
git add outputs-addition.tf tests/upgrade.tftest.hcl README.md
git diff --cached
git commit -m "Expose subnet names as an additive output"
git push -u origin add-subnet-names
gh pr create --base main --title "Add subnet_names output" \
  --body "Backward-compatible interface addition. No resource changes. Mock tests cover the map output."
```

Expected: **2 passed, 0 failed**. Review CI and the diff, then merge in GitHub.
Do not tag your unmerged feature branch.

## 2. Publish the new module release

```bash
git switch main
git pull --ff-only
git tag -a v1.1.0 -m "Network module v1.1.0 adds subnet_names"
git push origin v1.1.0
gh release create v1.1.0 --verify-tag \
  --title "Network module v1.1.0" \
  --notes "Adds subnet_names map output. Existing inputs and outputs are unchanged. No infrastructure changes are intended."
git show v1.0.0:outputs.tf
git show v1.1.0:outputs-addition.tf
```

v1.0.0 must still lack the new output. Publishing a release does not change the
live workspace's pinned Git ref.

## 3. Upgrade the consumer in a separate PR

```bash
cd "$LAB_HOME/azure-platform-live"
git switch main
git pull --ff-only
git switch -c upgrade-network-v1-1
```

Change **only the network** source suffix in `environments/dev/main.tf` from
`?ref=v1.0.0` to `?ref=v1.1.0`. Keep resource-group at v1.0.0.
Append to `environments/dev/outputs.tf`:

```hcl
output "subnet_names" {
  description = "Subnet names from network module v1.1.0."
  value       = module.network.subnet_names
}
```

```bash
terraform -chdir=environments/dev fmt
terraform -chdir=environments/dev init -backend=false
terraform -chdir=environments/dev validate
git diff -- environments/dev
git add environments/dev/main.tf environments/dev/outputs.tf
git commit -m "Adopt network v1.1.0 and expose subnet names"
git push -u origin upgrade-network-v1-1
gh pr create --base main --title "Upgrade network module to v1.1.0" \
  --body "Adopt the new Git ref and expose subnet_names. Expect only a root output addition, no Azure resource changes."
```

Changing the source ref makes init fetch the new module. `init -upgrade` is
sometimes useful for deliberate dependency upgrades, but it can also reconsider
providers within constraints; it is unnecessary here. Review any lock-file
diff rather than committing a surprise provider upgrade. The provider remains
4.50.0 and module versions are not stored in `.terraform.lock.hcl`.

## 4. Review the output-only run

Expect **0 add, 0 change, 0 destroy**, with a new root output map
`{app = "snet-app", data = "snet-data"}`. Terraform/HCP may describe this as
output-only state changes. After merging, review and confirm the normal run to
persist that output in HCP state; an output-only apply does not update Azure
network resources.

If a no-infrastructure-change run is presented as already finished, inspect
the state outputs and run details; queue the appropriate normal run to persist
pending output changes rather than assuming a speculative output was saved.

## Expected result and checkpoint

Two module release tags coexist, live explicitly selects v1.1.0, and state
exposes `subnet_names`. No resource replacement was needed.

**Exercise:** Before upgrading the Git ref, try `terraform validate` with the
new root output in a temporary uncommitted edit. Explain the unsupported
attribute error from a v1.0.0 child, then restore the intended v1.1.0 selection.

[Previous](08-deploy.md) | [Course index](../README.md) | [Next](10-drift.md)
