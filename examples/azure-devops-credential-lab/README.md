# Azure DevOps credential artifact lab

Two standalone pipelines compare a mock credential-bearing artifact with a
sanitized Terraform plan summary. This optional lab is separate from the HCP
Terraform course and pins Terraform 1.13.5 and AzureRM 4.49.0.

## Setup

Create two Azure DevOps pipelines using this repository and the published lab
branch. Select **Existing Azure Pipelines YAML file**, then choose
[`rg-demo-baseline.yml`](rg-demo-baseline.yml) for one pipeline and
[`rg-demo-fixed.yml`](rg-demo-fixed.yml) for the other. Both run manually.

The baseline needs no Azure access or Terraform extension. It checks out no
source and runs no Terraform commands. Its `client_secret` field contains only
the nonfunctional marker `DEMO_CANARY_NOT_AN_AZURE_CREDENTIAL`. Never replace
that marker with a real credential.

Before running the fixed pipeline:

1. Install the Azure DevOps Terraform tasks extension that supplies
   `TerraformInstaller@1` and `TerraformTaskV4@4`. Use a task version that
   supports both authentication inputs shown in the YAML.
2. In a dedicated training subscription, prepare an existing state resource
   group, storage account and private blob container. Create a lab Azure
   Resource Manager service connection, preferably with workload identity
   federation, and authorize only the fixed pipeline to use it.
3. Give its identity Storage Blob Data Contributor access to the state
   container, plus the Azure permissions needed to read the resource group
   during planning. Applying needs permission to create resource groups.
   Pre-register the required resource providers: automatic registration is
   disabled in [`main.tf`](main.tf).
4. Replace the four `REPLACE_WITH_...` variables in the fixed YAML with your lab
   service connection and backend names. Keep `tfDir` pointing to
   `$(Build.SourcesDirectory)/examples/azure-devops-credential-lab`.

Leave `apply` at its default `false` for artifact comparison. Planning contacts
Azure and uses remote state; it does not deploy the resource group. Setting
`apply: true` creates `rg-tf-auth-demo-fixed` in `westeurope`. If you opt in to
apply, remove that lab resource group afterward and reconcile Terraform state.
Keep the state storage until cleanup is complete.

## Compare the artifacts

| Pipeline artifact | Expected contents |
|---|---|
| `rg-demo-baseline-review` | `legacy-init.example.yml` and `simulated-legacy-backend.json`; the latter contains the mock marker |
| `rg-demo-fixed-review` | Only `plan-summary.json`, containing resource addresses and change actions |

The baseline's legacy init snippet is inert comparison text. Setting only
`use_azuread_auth=true` selects backend storage authentication; it does not by
itself keep credentials out of backend metadata.

The fixed init sets both `backendAzureRmUseEntraIdForAuthentication` and
`backendAzureRmUseEnvironmentVariablesForAuthentication` to `true`. It saves
the binary plan in the agent's temporary directory, applies it only when
requested on the same agent, and deletes it in an `always()` cleanup step.
It publishes only the allowlisted summary, excluding resource values.

Do not publish `.terraform`, state, binary plans, raw plan JSON, credentials,
or source attachments. Treat pipeline logs and remote state as restricted
data even when the published summary contains no resource values.
