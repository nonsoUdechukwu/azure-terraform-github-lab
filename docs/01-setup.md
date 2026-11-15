# 01 - Tools and your three repositories

[Previous](00-orientation.md) | [Course index](../README.md) | [Next](02-resource-group.md)

## Objectives

Install the baseline tools, create three empty public repositories, and learn
the difference between the course checkout and your independent module repos.

## 1. Prepare tools

Use macOS/Linux or WSL with Git, GitHub CLI (`gh`), Azure CLI (`az`), Terraform
**1.15.3**, and a text editor. Follow the vendor installers:
[Git](https://git-scm.com/downloads),
[GitHub CLI](https://cli.github.com/),
[Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli),
[Terraform](https://developer.hashicorp.com/terraform/install).
Choose 1.15.3 from the
[versioned release directory](https://releases.hashicorp.com/terraform/1.15.3/);
verify its published checksum before installing. An unversioned package-manager
install may select a newer release and fail the live root's exact constraint.

In your terminal:

```bash
git --version
gh --version
az version
terraform version
gh auth login
gh auth status
```

Set Git's author name/email if not already configured:
`git config --global user.name "Your Name"` and
`git config --global user.email "YOUR_VERIFIED_OR_GITHUB_NOREPLY_EMAIL"`.
These identify commits; they are not Azure credentials.

## 2. Create a course folder and define two useful paths

Run these commands in one terminal. If you open a new terminal later, set
`LAB_HOME` and `COURSE` again to the same absolute paths.

```bash
mkdir -p "$HOME/terraform-teaching-lab"
export LAB_HOME="$HOME/terraform-teaching-lab"
cd "$LAB_HOME"
git clone https://github.com/nonsoUdechukwu/azure-terraform-github-lab.git course
export COURSE="$LAB_HOME/course"
```

Do not nest your learner repositories inside the course repository.
`$COURSE/examples/...` is a source to read/copy, never the deployment checkout.

## 3. Create your own repositories

On GitHub, choose **New repository** three times. Use your own account, select
**Public**, and leave README, license and `.gitignore` initialization unchecked:

| Repository | Purpose |
|---|---|
| `terraform-azurerm-resource-group` | Reusable resource-group module |
| `terraform-azurerm-network` | Reusable network module |
| `azure-platform-live` | Environment configuration and reviewed changes |

Public module repos allow HCP workers to download the Git sources without extra
private-clone credentials. Public code is readable by everyone. Do not copy
production configuration into it. These names also suit the optional registry
naming convention `terraform-PROVIDER-NAME`.

Initialize independent local repositories; replace the username once:

```bash
export GITHUB_USER="YOUR_GITHUB_USER"
cd "$LAB_HOME"
mkdir terraform-azurerm-resource-group terraform-azurerm-network azure-platform-live
cd "$LAB_HOME/terraform-azurerm-resource-group"
git init -b main
git remote add origin "https://github.com/$GITHUB_USER/terraform-azurerm-resource-group.git"
cd "$LAB_HOME/terraform-azurerm-network"
git init -b main
git remote add origin "https://github.com/$GITHUB_USER/terraform-azurerm-network.git"
cd "$LAB_HOME/azure-platform-live"
git init -b main
git remote add origin "https://github.com/$GITHUB_USER/azure-platform-live.git"
```

Do not run `gh repo create` against the course owner's account; you are creating
your own repos through the UI. No Azure resource or identity has been created.

## 4. Add safe ignore rules before writing Terraform

Create `.gitignore` in **each** learner repository with:

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
crash.*.log
*.tfvars
*.tfvars.json
!terraform.tfvars.example
.env
*.pem
*.key
.DS_Store
```

In the **two module repos only**, append `.terraform.lock.hcl`. Consumers
select providers, so this lab does not commit library-module lock files.
In the **live repo only**, append
`!environments/dev/terraform.tfvars`. This explicitly allows the one reviewed,
non-secret variables file from lesson 05. Do not unignore every `*.tfvars`.
The live `.terraform.lock.hcl` **must** be committed later.

## Expected result and checkpoint

Run `git remote -v` and `git status --short` in each learner directory. Each
remote must be a different repo under your username; each has its own `.git/`.
The first push happens after you author the modules, not yet.

**Exercise:** Explain why copying the course's entire `.git/` directory into a
module repository would be wrong. Check that you can locate all four local
directories (`course` plus your three repos).

[Previous](00-orientation.md) | [Course index](../README.md) | [Next](02-resource-group.md)
