# 07: Costs, safety and cleanup

## Before any optional Azure practice

1. Pick your own maximum acceptable spend and stop date. This lab does not
   prescribe a limit. Use a dedicated training subscription and a resource
   group containing **only disposable lab resources**; check access with your
   administrator. Never run cleanup against shared or production resources.
2. Estimate each chosen service in the
   [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/):
   Databricks DBUs and underlying compute, storage/transactions, ADF activity
   and integration runtime, Azure SQL compute/storage/backups, network egress,
   logging and any private networking. Prices vary by region, tier and time.
   Free trials/credits have eligibility and expiry conditions.
3. In Azure portal open **Cost Management + Billing → Budgets → Add** for
   the intended subscription/resource-group scope. Set your chosen amount,
   period, actual/forecast thresholds and reachable email. Also inspect cost
   analysis, quotas and resource inventory. [Budget documentation](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets).
   **Budgets are alerts, not hard spending limits:** they do not stop resources,
   billing data is delayed, and charges can exceed the amount before an alert.
4. Record resource group, workspace, Databricks-managed resource group, storage
   account, factory, SQL server/database, connector, identities and any
   out-of-group resources. Set a calendar reminder to clean up. Avoid schedules,
   long-lived clusters and optional paid networking/monitoring unless you
   explicitly budget for them.

## At the end of each Azure session

1. In ADF disable/delete any triggers, cancel active pipeline runs and verify no
   new runs are queued. Stop Databricks jobs and classic compute, delete any
   schedules, and check SQL activity. Serverless and SQL storage may still
   incur charges; stopping compute is **not** complete cleanup.
2. In Databricks delete the lab job and imported notebook. If an external volume
   was created, drop the lab schema only after verifying it contains no data
   to keep:

   ```sql
   DROP SCHEMA IF EXISTS `YOUR_CATALOG`.retail_lab CASCADE;
   ```

   Replace the catalog with your actual catalog. Dropping an **external**
   volume unregisters it; its underlying ADLS files remain. Remove lab-specific
   external location/storage credential and grants only if dedicated to this
   lab and not used elsewhere. Do not remove shared Unity Catalog objects.
3. In Azure portal open your dedicated lab resource group, inspect its contents
   and dependencies, then select **Delete resource group** and confirm its
   exact name. This is irreversible: it removes contained storage data, ADF,
   the SQL database, workspace and connector. Databricks manages a separate
   resource group; the workspace deletion normally removes managed resources.
   Verify rather than deleting an unidentified managed group manually.

   Alternatively, after confirming subscription and resource-group name:

   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   az account show --query '{name:name,id:id}' -o table
   az group show --name "YOUR_DEDICATED_LAB_RG" -o table
   az resource list --resource-group "YOUR_DEDICATED_LAB_RG" -o table
   # Only after confirming every listed resource is disposable:
   az group delete --name "YOUR_DEDICATED_LAB_RG" --yes
   az group exists --name "YOUR_DEDICATED_LAB_RG"
   ```

   Expected last output: `false` after deletion completes. Do not use
   `--no-wait` if you want to wait for completion. If deletion is blocked,
   inspect locks and permissions; do not remove shared locks blindly.
4. In portal, check both the lab and recorded Databricks-managed resource group
   are gone, and inspect subscription resources for anything created outside
   them (including access connectors, diagnostics, private endpoints and
   public IPs). Remove only dedicated lab resources. Check retained Azure SQL
   backups/long-term retention and soft-deleted storage/recovery resources under
   the actual service's retention policy; retained data can persist or incur
   charges. Remove dedicated role assignments and identities if still present.
   Review cost analysis for several days because usage reporting is delayed.
   Remove or adjust the lab budget only after you no longer need its alerts.

For Free Edition cleanup, follow lesson 02: delete the job/notebook and drop
only the lab schema. Local cleanup is to delete the generated `retail.db` from
`data-engineering-lab/` and any specifically named `/tmp/retail-lab-*`
experiment files/directories you created. Never delete the repository or a
shared directory.
