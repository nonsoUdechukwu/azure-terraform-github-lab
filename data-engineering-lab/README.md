# Retail data engineering lab

Build a synthetic retail pipeline, from raw events to a dimensional sales report.
Start locally for free; optionally repeat the pipeline on Databricks Free Edition
and then on Azure. No Azure resource is created by the local exercises or CI.
This lab is independent of the Terraform course in the repository root.

## Route and pace

Set aside 3–5 hours per week. Times are estimates; repeat a lesson if needed.
Cloud interfaces and quotas change, so check the linked primary documentation.

| Week | Lesson | Time | Cost and result |
|---|---|---:|---|
| 1 | [01: Python, SQL and modelling](lessons/01-local.md) | 3–5 h | Free; run and query the local pipeline |
| 2 | [02: Spark, Parquet and Delta](lessons/02-databricks.md) | 3–5 h | Free Edition; build and rerun medallion tables |
| 3 | [03: Administration and security](lessons/03-admin.md) | 3–5 h | Free concepts and workspace exercises; Azure admin is optional |
| 4 | [04: Azure Data Factory](lessons/04-azure-adf.md) | 3–5 h | Optional, paid Azure ingestion and orchestration |
| 5 | [05: Azure SQL performance](lessons/05-azure-sql.md) | 3–5 h | Optional, paid Azure SQL experiments |
| 6 | [06: Git, CI and capstone](lessons/06-capstone.md) | 3–5 h | Free local/CI; optional cloud deployment |

Use the [cost and cleanup checklist](lessons/07-cost-cleanup.md) **before**
creating anything in Azure and immediately after each Azure session. Choose
your own spending limit first; this course does not assume one. Estimate the
region, SKU and duration with the [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/).
Budgets alert; they do **not** cap or stop spending, and reporting is delayed.

## What runs where

| Capability | Local Python + SQLite | Databricks Free Edition | Optional Azure |
|---|---|---|---|
| Retail pipeline, SQL, tests | Yes, offline | Notebook with Spark and Delta | Azure Databricks notebook |
| Unity Catalog, volume, job | No | Workspace-scoped practice subject to privileges/quotas | Full admin subject to SKU/permissions |
| ADF, Azure SQL, managed identity, networking | No | No; not an Azure subscription | Yes; separately billed |
| CI | GitHub Actions or local unittest | No cloud connection required | Manual deployment after review |

Free Edition is a separate non-commercial Databricks offering, **not** an Azure
Databricks workspace in your subscription and not an Azure free trial. It has
serverless-only compute, restricted outbound internet, quotas, one workspace and
metastore, and no account console, SSO/SCIM, custom storage, private networking,
or classic compute. It has no SLA. Quotas can pause compute until reset. Azure
Data Factory, Azure SQL, Azure managed identity and Azure networking require
separate Azure resources; Free Edition does not supply or pay for them.
[Current Free Edition limits](https://learn.microsoft.com/en-us/azure/databricks/getting-started/free-edition-limitations).

## Prerequisites

- macOS/Linux shell or Windows WSL; Python **3.9+**, Git and a GitHub account.
  No third-party Python packages, Spark installation, or Azure account needed for week 1.
- For week 2, a [Databricks Free Edition account](https://www.databricks.com/learn/free-edition),
  browser, and permission to create a schema and volume in an existing catalog.
- Optional Azure: a dedicated subscription/resource group, permissions to create
  and delete resources and assign roles, plus Azure CLI for the cleanup commands.
  Never use production data, production subscriptions, passwords in Git, or shared
  resources for the destructive cleanup.

From your clone's root:

```bash
cd data-engineering-lab
python3 --version
python3 -m unittest discover -s tests -v
python3 src/pipeline.py
```

Expected: three tests pass and `bronze=9 silver=6 quarantine=2 gold_groups=6`.
The generated `retail.db` is ignored by Git. Run commands from this lab directory
unless a lesson says otherwise. The local pipeline is a teaching implementation,
not a production data platform.

## Data contract and design

`data/orders.csv` contains one **event** per `event_id`, potentially multiple
events per order. `E007` updates order `O002`; `E008` has negative quantity;
`E009` references an unknown customer. Dimensions are current snapshots, not
historical slowly changing dimensions. Bronze preserves raw events keyed by
event ID; silver selects the latest *valid* event per order using
`updated_at`, then `event_id` as deterministic tie-breaker; quarantine holds
invalid events; gold aggregates by date, region and category. Latest-invalid
events do not cancel earlier valid ones. No deletes or late dimension history
are modelled. Prices are dollars with at most two decimal places. Local SQL
stores integer cents, whereas Spark uses decimal dollars.

The local and Spark implementations teach the same baseline but have different
numeric limits and invalid-data checks; don't assume they are production-equivalent
validators. Rerunning the same full dataset leaves results unchanged. A new
event is incrementally merged into bronze, but silver/quarantine/gold are
recomputed from all bronze; this is intentionally small-scale, not a scalable
incremental processing design.

## Contents

- `data/`: synthetic CSV inputs
- `src/pipeline.py`, `tests/`: runnable offline pipeline and tests
- `sql/analysis.sql`, `sql/azure_sql.sql`: runnable queries
- `databricks/retail_notebook.py`: importable Databricks source notebook
- `.github/workflows/data-engineering-lab-ci.yml` at repository root: test-only CI

The local path and tests are verified locally. Neither Databricks nor paid Azure
integrations have been deployed or validated by the course author in this workspace.
