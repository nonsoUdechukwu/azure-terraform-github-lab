# 07 - Connect Azure with HCP-native OIDC

[Previous](06-hcp.md) | [Course index](../README.md) | [Next](08-deploy.md)

## Objectives

Bootstrap an Entra application/service principal, grant the training identity
Azure permissions, and trust only this HCP workspace's plan/apply identities.
These are deliberate administrator actions, not operations performed by course CI.

## 1. Confirm authority and choose the training subscription

The human performing this section needs:

- Entra permission to create applications and service principals (tenant
  settings may restrict this).
- Azure permission to create role assignments, such as Owner, User Access
  Administrator, or Role Based Access Control Administrator at the chosen scope.
- Permission to register resource providers on the subscription.

These are separate permissions. Do not ask for a production-wide role to bypass
a training-account restriction. Use a dedicated training subscription.

```bash
az login
az account list --query "[].{Name:name,Id:id}" -o table
export SUBSCRIPTION_ID="YOUR_TRAINING_SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"
export TENANT_ID="$(az account show --query tenantId -o tsv)"
export HCP_ORG="YOUR_EXACT_HCP_ORGANIZATION_NAME"
```

Keep actual identifiers and command responses in private notes, not in this
public repository. Confirm the selected subscription in the portal too.

## 2. Register the network provider once, as the human

```bash
az provider register --namespace Microsoft.Network --wait
az provider show --namespace Microsoft.Network --query registrationState -o tsv
```

Expected: `Registered`. The root's `resource_provider_registrations = "none"`
means remote Terraform will not attempt broad automatic registration.

## 3. Create the application and its service principal

```bash
export APP_CLIENT_ID="$(az ad app create \
  --display-name terraform-lab-hcp-dev --query appId -o tsv)"
export APP_OBJECT_ID="$(az ad app show --id "$APP_CLIENT_ID" --query id -o tsv)"
export SP_OBJECT_ID="$(az ad sp create --id "$APP_CLIENT_ID" --query id -o tsv)"
```

Run once and stop on any error. Do not rerun creation blindly: check Entra App
registrations/Enterprise applications for partial creations first.
No client secret is generated.

| Value | Used for |
|---|---|
| Application/client ID (`appId`) | HCP `TFC_AZURE_RUN_CLIENT_ID` |
| Application object ID (`id`) | Managing this app's federated credentials |
| Service-principal object ID (`id`) | Azure RBAC role assignment |

An application and service principal are related but **not the same directory
object**. Confusing their IDs is a common bootstrap failure.

## 4. Grant the lab role

```bash
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role Contributor \
  --scope "/subscriptions/$SUBSCRIPTION_ID" \
  --query id -o tsv
```

Record the returned role-assignment ID privately for cleanup. Subscription
Contributor is intentionally broad **only for a dedicated training subscription**
because this root creates its own resource group. It does not grant role
assignment administration.

Production alternative: have a bootstrap administrator create the RG and grant
the deployment identity a narrower RG-scoped role/custom role. Then redesign
this root so it does not create that RG (use an existing-RG input/data source),
or explicitly import/manage it under an approved state/permission design.
Merely scoping this exact root to an RG that does not exist will fail. Migrating
ownership of an already-managed RG requires a reviewed state/import plan; do
not casually remove it from code and apply.

For teaching simplicity plan/apply use the same identity. A hardened design can
separate plan/read and apply/write identities after checking required read/data
source permissions; that is outside this baseline.

## 5. Create one federated credential per run phase

In Entra **App registrations > terraform-lab-hcp-dev > Certificates & secrets >
Federated credentials > Add credential > Other issuer**, create:

| Field | Plan credential |
|---|---|
| Name | `hcp-dev-plan` |
| Issuer | `https://app.terraform.io` |
| Subject | `organization:YOUR_ORG:project:Terraform-Labs:workspace:azure-platform-dev:run_phase:plan` |
| Audience | `api://AzureADTokenExchange` |

Replace `YOUR_ORG` with the exact HCP organization name, no placeholder/brackets.
Create a second credential named `hcp-dev-apply` with the same issuer/audience
and a subject ending `run_phase:apply`.

The issuer has **no trailing slash**. The project/workspace names and case
must match exactly. Both credentials trust **HCP Terraform**, not GitHub's
`token.actions.githubusercontent.com`. GitHub stores code; HCP executes Azure
operations in this design.

CLI alternative, if you prefer the same deliberate operation in your terminal:

```bash
az ad app federated-credential create --id "$APP_OBJECT_ID" --parameters "{
  \"name\": \"hcp-dev-plan\",
  \"issuer\": \"https://app.terraform.io\",
  \"subject\": \"organization:$HCP_ORG:project:Terraform-Labs:workspace:azure-platform-dev:run_phase:plan\",
  \"audiences\": [\"api://AzureADTokenExchange\"]
}"
az ad app federated-credential create --id "$APP_OBJECT_ID" --parameters "{
  \"name\": \"hcp-dev-apply\",
  \"issuer\": \"https://app.terraform.io\",
  \"subject\": \"organization:$HCP_ORG:project:Terraform-Labs:workspace:azure-platform-dev:run_phase:apply\",
  \"audiences\": [\"api://AzureADTokenExchange\"]
}"
```

Use the portal **or** CLI, not both. Inspect both credentials after creation.

## 6. Configure HCP environment variables

Open `azure-platform-dev > Variables`. Add these as **Environment variables**:

| Key | Value |
|---|---|
| `TFC_AZURE_PROVIDER_AUTH` | `true` |
| `TFC_AZURE_RUN_CLIENT_ID` | Your application/client ID, not either object ID |
| `ARM_SUBSCRIPTION_ID` | Your training subscription ID |
| `ARM_TENANT_ID` | Your tenant ID |

These identifiers are not passwords, but keep them out of public screenshots.
You may mark them sensitive to limit UI display. No Azure credential is placed
in GitHub Actions secrets in this core course.

For this **native single-provider configuration**, do **not** manually set
`ARM_CLIENT_ID`, `ARM_USE_OIDC`, `ARM_OIDC_TOKEN`, `client_id`, `use_oidc`,
`oidc_token`, or a client secret. HCP injects its native dynamic credentials.
Check inherited variable sets too if conflicting settings already exist.

## Expected result and checkpoint

The app has two federated credentials and its service principal has the
intended training role. HCP has four environment variables. Role/federation
propagation can take time; if a run immediately fails, inspect the exact error
and allow propagation before retrying.

**Exercise:** Predict the failure if you move the workspace to another HCP
project without updating its federated subjects. Explain why a successful plan
doesn't prove the apply-phase federation exists.

Primary source:
[Azure dynamic provider credential configuration](https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/azure-configuration).

[Previous](06-hcp.md) | [Course index](../README.md) | [Next](08-deploy.md)
