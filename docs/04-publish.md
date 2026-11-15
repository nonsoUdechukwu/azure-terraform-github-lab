# 04 - Publish immutable module releases

[Previous](03-network.md) | [Course index](../README.md) | [Next](05-live.md)

## Objectives

Understand commit vs branch vs tag vs GitHub Release, and publish v1.0.0 for
each module without moving existing tags.

## 1. Check readiness

Open each repo in GitHub and confirm its latest default-branch CI run passed.
In each local clone, run `git status --short`; it should print nothing.
Do not release uncommitted changes or a branch whose tests failed.

A branch such as `main` moves as you commit. An annotated Git tag gives a named
release point with a message. A GitHub Release adds human-readable release notes
to that tag. Consumers download the Git source at the tag; a GitHub Release is
useful documentation but is not required for Git-source resolution.

## 2. Tag and release the resource-group module

```bash
cd "$LAB_HOME/terraform-azurerm-resource-group"
git switch main
git pull --ff-only
git log -1 --oneline
git tag -a v1.0.0 -m "Resource-group module v1.0.0"
git show v1.0.0 --stat
git push origin v1.0.0
gh release create v1.0.0 --verify-tag \
  --title "Resource-group module v1.0.0" \
  --notes "Initial release: resource group with configurable name, location and tags; name, location and id outputs; mocked tests."
```

If Git says the tag already exists, inspect `git show v1.0.0` and GitHub Releases.
Do not delete/recreate or force-push it to make a command succeed.

## 3. Tag and release the network module

```bash
cd "$LAB_HOME/terraform-azurerm-network"
git switch main
git pull --ff-only
git log -1 --oneline
git tag -a v1.0.0 -m "Network module v1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --verify-tag \
  --title "Network module v1.0.0" \
  --notes "Initial release: VNet and standalone subnet map; vnet_id and subnet_ids outputs; implicit default outbound disabled."
```

## 4. Verify what a caller will download

Replace the username or use `$GITHUB_USER` from lesson 01:

```bash
git ls-remote --tags "https://github.com/$GITHUB_USER/terraform-azurerm-resource-group.git" 'refs/tags/v1.0.0*'
git ls-remote --tags "https://github.com/$GITHUB_USER/terraform-azurerm-network.git" 'refs/tags/v1.0.0*'
```

An annotated tag normally shows the tag object and a peeled `^{}` commit line.
Open GitHub's tag selector, select v1.0.0, and inspect its files. The network
version must **not** expose `subnet_names` yet.

## 5. Understand version guarantees

We treat published tags as immutable by convention. A Git hosting administrator
can still move a tag unless repository rules prevent it. Where available, add
tag rules preventing update/deletion of `v*`. A reviewed full commit SHA is
stronger pinning than a mutable branch or tag name.

Use major/minor/patch deliberately: `v1.0.1` for a compatible fix, `v1.1.0` for
an additive output, `v2.0.0` for removing/renaming a required interface.
Never silently change old releases to fix downstream consumers.

## Expected result and checkpoint

Both repositories have annotated v1.0.0 tags and GitHub Releases with useful
notes. Copy their GitHub URLs into your own private learning notes.

**Exercise:** Which action updates existing consumers: pushing a new module
commit, adding a new release, or changing the consumer's pinned source and
applying a reviewed plan? Explain why only the last is a deliberate adoption.

[Previous](03-network.md) | [Course index](../README.md) | [Next](05-live.md)
