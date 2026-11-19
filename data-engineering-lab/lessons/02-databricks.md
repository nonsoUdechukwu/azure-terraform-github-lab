# 02: Spark, Parquet, Delta and medallion

**Goal:** run the supplied notebook on Databricks Free Edition. Time: 3–5 hours.
No Azure subscription is required. UI labels may change.

## 1. Prepare the workspace

1. Sign up for [Free Edition](https://www.databricks.com/learn/free-edition)
   and open its workspace. Read the [limitations](https://learn.microsoft.com/en-us/azure/databricks/getting-started/free-edition-limitations).
2. Open **Catalog**. Identify an existing catalog in which you can create
   schemas (often `workspace`; do not assume the name). Create schema
   `retail_lab`, then create a **managed volume** named `files` within it.
   If permission is denied, use a catalog where you have `USE CATALOG` and
   `CREATE SCHEMA`; do not try to create cloud credentials in Free Edition.
3. Open that volume and upload `data/orders.csv`, `data/customers.csv`, and
   `data/products.csv` directly into its root. Copy its displayed path, e.g.
   `/Volumes/workspace/retail_lab/files`. Names are case-sensitive.
4. In **Workspace**, import `databricks/retail_notebook.py` as a source
   notebook. Open it and attach/select serverless compute. Set the notebook
   widgets `catalog` to your actual catalog, `schema` to `retail_lab`, and
   `volume_path` to the copied path. Select **Run all**.
   If widgets are not visible yet, run the first code cell, set them, then
   run all. Do not mix datasets from a previous experiment into this volume.

Expected output: `bronze, silver, quarantine, gold groups: 9 6 2 6`,
`total revenue: 77.00`, `parquet rows: 6`. Run all a second time: counts
and total must not change. Check `quarantine_orders` in Catalog to find E008
and E009. `DESCRIBE HISTORY` displays Delta commits; extra commits on rerun
do not mean extra business rows.

## 2. Understand the code

A Spark DataFrame is a distributed table-like plan, not a Python list.
Transformations (`select`, `filter`, `join`, `groupBy`) are lazy; an action
such as `count` triggers work. The notebook reads CSV as strings, checks IDs,
uses safe casts and validates records, ranks valid versions by timestamp and
event ID, then merges one row per order. Spark's window uses
`row_number`, just as the SQL lesson does. Explore it:

```python
display(spark.table(f"{namespace}.silver_orders").orderBy("order_id"))
display(spark.table(f"{namespace}.quarantine_orders"))
```

Bronze stores raw events, Silver has cleaned current orders, Gold has grouped
revenue. Quarantine prevents bad records from contaminating silver while
retaining them for investigation. The notebook selects the latest *valid*
event, so an invalid newer event doesn't delete an older valid order.

Parquet is a columnar file format with compression and column pruning. The
notebook writes a Parquet folder and reads it back. Delta uses Parquet files
**and** a transaction log (`_delta_log`) with commits and metadata, allowing
atomic changes, schema enforcement, history and `MERGE`. A raw Parquet folder
doesn't have Delta's transactional guarantees. In Catalog, inspect schema and
history; never manually edit the Delta log.

## 3. Incremental exercise

1. Download/copy the three CSV files to a **temporary** folder on your computer.
   Append this line to the copy of `orders.csv`:
   `E010,O001,C001,P001,2025-01-02,3,5.00,2025-01-06T10:00:00`
2. Replace the volume's `orders.csv` with your copy. Run all twice.
   Expected: bronze 10, silver 6, quarantine 2, gold groups 6, total 82.00.
3. Replace the uploaded file with the original if you want, but note this alone
   does not remove E010 from bronze. For a clean reset, drop this lab schema
   only after following the cleanup section below, recreate its volume, upload
   the original files, and rerun.

Both merges rely on unique event IDs in each batch and stable order IDs.
`WHEN NOT MATCHED BY SOURCE DELETE` is safe here only because silver's source
is a **complete recomputation from bronze**, not a partial batch. Do not copy
that delete clause into a partial-incremental production job. Dimension
snapshots can reclassify historical facts; this is not SCD type 2.

## 4. Jobs, monitoring and cleanup

Create a one-task job pointing to this notebook, pass the same three widget
parameters, and run it **once**; do not enable a schedule. Inspect the job run
and task output. A failed task should show its exception; fix the input and
rerun, rather than silently accepting missing data. Delete the job afterward.

Remove this lab's schema and managed objects in Catalog, or in a SQL notebook
after replacing `YOUR_CATALOG` with your actual simple catalog name:

```sql
DROP SCHEMA IF EXISTS `YOUR_CATALOG`.retail_lab CASCADE;
```

This deletes the volume's input and Parquet output and the managed lab tables.
Only run it against the lab schema you created. Delete the imported notebook
separately. If compute is unavailable, check quota before retrying. If CSV
paths fail, check volume path and upload names; if access fails, check catalog,
schema and volume privileges. Spark/Delta examples:
[Spark DataFrames](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html),
[Delta tutorial](https://learn.microsoft.com/en-us/azure/databricks/delta/tutorial),
[volumes](https://learn.microsoft.com/en-us/azure/databricks/volumes/).
