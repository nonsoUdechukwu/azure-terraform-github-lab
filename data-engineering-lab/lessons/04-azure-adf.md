# 04: Optional Azure Data Factory ingestion and orchestration

**Paid Azure exercise.** Do not start until you choose a spending limit, estimate
cost, create alerts, and read [cleanup](07-cost-cleanup.md). ADF activity runs,
Azure storage, Databricks compute and networking can all cost money. Budget
alerts do not stop usage. This exercise was not cloud-validated here.
Time: 3–5 hours. Free Edition cannot replace the Azure workspace in this lesson.

## 1. Create a small, isolated environment

1. In a dedicated training subscription, create a uniquely named resource
   group in an available region. Record subscription ID, region and resource
   group name. Use it for all resources below, not for anything you want to keep.
2. Create an Azure Storage account with hierarchical namespace enabled (ADLS
   Gen2), an Azure Data Factory, and an Azure Databricks workspace in compatible
   regions. Use the smallest supported configuration that you have priced.
   Record the Databricks-managed resource group as well.
3. In the storage account create a private container `retail`. Under it upload
   all three lab CSVs to `source/` (three separate blobs). Never enable anonymous
   access. Create an empty `landing/` folder if the UI requires it.
4. In Data Factory **Manage → Managed identities**, identify the factory's
   system-assigned identity. In the storage account **Access control (IAM)**,
   grant that identity **Storage Blob Data Contributor** scoped to the lab
   container (or account if container scope is unavailable). RBAC propagation
   can take time. In ADF Studio, create an Azure Data Lake Storage Gen2 linked
   service using system-assigned managed identity; test the connection.

## 2. Copy the three files

1. In ADF Studio create a binary dataset for the ADLS linked service, container
   `retail`, parameterized `folder` and `filename`. Binary copy preserves the
   original CSV bytes. Set the directory and filename to the dataset parameters.
2. Create a pipeline `retail_ingest` and three **Copy data** activities.
   For each activity use the same binary dataset as both source and sink, with:

   | Activity | Source folder | Sink folder | Filename |
   |---|---|---|---|
   | CopyOrders | source | landing | orders.csv |
   | CopyCustomers | source | landing | customers.csv |
   | CopyProducts | source | landing | products.csv |

   Set filename in both source and sink dataset parameters. Connect the
   activities sequentially with **On success**, so a later step doesn't run
   after a failure. Leave retries at zero for the first debug run.
3. Select **Debug** and inspect the output of each activity. Expected: three
   successful copy activities, one file each. Open `landing/` in Storage
   browser and confirm all three names. **Publish all** only when ready.
   No trigger or recurring schedule is needed.
4. Deliberately change one source filename to a nonexistent file; debug again.
   The failing activity should report an error and downstream success-dependent
   activities should not run. Restore the name and rerun. In **Monitor**, inspect
   activity input, output, duration and error. Debug runs and published
   pipeline runs can appear in different monitoring views; don't mistake an old
   success for the current run.

## 3. Connect the copied data to Databricks

The ADF sink and the notebook must point to the **same storage path**; simply
uploading CSVs to an unrelated managed volume does not automate ingestion.
This section requires Unity Catalog administration and Azure role assignments:

1. Create an Azure Databricks access connector with managed identity. Grant
   it Storage Blob Data Contributor on the `retail` container. Follow
   [the official ADLS setup](https://learn.microsoft.com/en-us/azure/databricks/getting-started/starter-journey/access-your-data/cloud-object-storage/azure)
   to create a UC storage credential and external location for
   `abfss://retail@STORAGE_ACCOUNT.dfs.core.windows.net/`, replacing the
   account placeholder with your actual name. Use an existing suitable UC
   catalog and create schema `retail_lab`; you need UC privileges including
   `CREATE EXTERNAL VOLUME` on the external location.
2. In a Databricks SQL editor, replace the catalog and account placeholders:

   ```sql
   CREATE EXTERNAL VOLUME `YOUR_CATALOG`.retail_lab.landing
   LOCATION 'abfss://retail@STORAGE_ACCOUNT.dfs.core.windows.net/landing';
   ```

   Grant the notebook's execution identity the necessary catalog/schema,
   table and volume privileges, including `READ VOLUME` and `WRITE VOLUME`
   (the notebook writes its Parquet demonstration there).
3. Import the notebook from lesson 02 into this **Azure** workspace. Run it
   once with `catalog=YOUR_CATALOG`, `schema=retail_lab`, and
   `volume_path=/Volumes/YOUR_CATALOG/retail_lab/landing`. Expected baseline
   is 9/6/2/6 and 77.00. The CSVs are now those copied by ADF.

## 4. Orchestrate and observe

1. Configure an Azure Databricks linked service in ADF using a supported managed
   identity authentication and suitable Unity Catalog-compatible job compute.
   The factory identity must be authorized in both Azure and the Databricks
   workspace/UC; consult the
   [linked-service tutorial](https://learn.microsoft.com/en-us/azure/data-factory/transform-data-using-databricks-notebook)
   for current identity/compute prerequisites.
2. Add a **Databricks Notebook** activity after CopyProducts, with an **On
   success** dependency. Select that linked service, the imported notebook's
   absolute workspace path, and base parameters `catalog`, `schema`, and
   `volume_path` as above. These names match the notebook widgets.
3. Debug once; inspect each copy and notebook activity in ADF and the associated
   Databricks run. Expected final table counts and total match step 3. Run
   again and verify unchanged business results. Test a bad filename again and
   confirm the notebook is skipped. Publish the corrected pipeline, run once
   manually, and inspect its run in Monitor. Do not add a schedule.

If you lack UC or identity privileges, stop at step 2; do not substitute a
personal token or claim an automated end-to-end integration. For permission
errors verify both Azure data-plane role and UC privileges; check firewall
rules, region compatibility, role propagation, notebook path, and compute mode.
Complete cleanup the same day. References:
[Copy activity](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview),
[notebook activity](https://learn.microsoft.com/en-us/azure/data-factory/transform-data-databricks-notebook)
and [ADF monitoring](https://learn.microsoft.com/en-us/azure/data-factory/monitor-visually).
