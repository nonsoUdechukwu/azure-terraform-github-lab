# 03: Databricks administration and security

**Goal:** connect your Azure knowledge to Databricks concepts and practise
what Free Edition permits. Time: 3–5 hours.

## 1. Map the components

Draw this hierarchy: account → workspace → catalog → schema → table/volume.
Unity Catalog (UC) centralizes governance; tables hold tabular data, volumes
hold non-tabular files. A catalog contains schemas; schema objects have
three-part names. Workspace permissions control workspace objects; UC
privileges separately control data. A SQL warehouse runs SQL, whereas notebook
compute runs notebook workloads. A job schedules or runs tasks and records
their results. Delta history records table changes, not all user activity.

## 2. Explore Free Edition

1. In Catalog, open your `retail_lab` schema and inspect a table's columns,
   owner, permissions and history. Observe that its dimensions and facts belong
   to the same schema; naming a catalog alone does not grant data access.
2. In your notebook, run `SELECT current_user(), current_catalog(), current_schema()`
   in a SQL cell. Use the actual catalog in lesson 02, not an assumed one.
3. Open the job run from lesson 02 or run it once again. Find its duration,
   task status and error output. Delete the job; do not schedule it.
4. Sketch a least-privilege model: a reader needs `USE CATALOG`, `USE SCHEMA`
   and `SELECT` on the relevant tables; a volume reader also needs
   `READ VOLUME`. A writer additionally needs appropriate write privileges.
   The job principal needs access to its notebook, compute and data.
   Do not grant `ALL PRIVILEGES` just to make a demo work.

Free Edition is not an enterprise admin sandbox: it lacks account console,
SSO/SCIM, private networking, custom workspace storage and classic compute.
Do not treat UI exercises as evidence of Azure tenant configuration.

## 3. Optional Azure administration walkthrough

Only after choosing a budget and reading [cleanup](07-cost-cleanup.md), create
an Azure Databricks workspace using the
[Azure quickstart](https://learn.microsoft.com/en-us/azure/databricks/getting-started/quick-start).
Follow current region, SKU and permission requirements. In a dedicated resource
group, note both the workspace and Databricks-managed resource group names.
Don't manually modify/delete managed resources while the workspace exists.

1. Compare Microsoft Entra authentication, workspace users/groups and
   service principals; identity is not the same as authorization. Provision a
   dedicated job identity and use short-lived credentials/managed identity
   where the integration supports them. Never commit tokens.
2. Inspect workspace compute policies, serverless availability, job compute
   and auto-termination. Compute, storage and network traffic can all incur
   charges. Stop unused classic compute and unschedule jobs.
3. Inspect Unity Catalog's metastore, catalog, schema, storage credential,
   external location, volume and grants. An Azure access connector managed
   identity needs Azure Storage data-plane RBAC **and** UC privileges; one
   doesn't replace the other. See
   [connect ADLS](https://learn.microsoft.com/en-us/azure/databricks/getting-started/starter-journey/access-your-data/cloud-object-storage/azure).
4. Inspect workspace/job run history and, where available and authorized,
   system tables/audit logs and Azure Monitor. Check failed runs, runtimes,
   identity and cost trends; avoid exposing logs or credentials. Availability
   varies by account, region and SKU.
5. Review network exposure, private endpoints, encryption, key management and
   access control without enabling extra paid services by default. Private
   networking and security controls are Azure-only, not Free Edition features.

**Checkpoint:** explain why Azure RBAC and UC grants are separate, why a
service principal is preferable to a personal token for automation, and where
to find a failed job's error. Complete cleanup at the end of the session.
References: [Unity Catalog](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/),
[security](https://learn.microsoft.com/en-us/azure/databricks/security/),
[jobs](https://learn.microsoft.com/en-us/azure/databricks/jobs/).
