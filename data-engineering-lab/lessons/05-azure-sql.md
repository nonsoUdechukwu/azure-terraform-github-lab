# 05: Optional Azure SQL and performance

**Paid Azure exercise.** First choose a spending limit, estimate the database,
storage and network costs and read [cleanup](07-cost-cleanup.md). Azure SQL
is a different service from Databricks SQL. Time: 3–5 hours. This lesson and
its T-SQL were not run against Azure SQL in this workspace.

## 1. Create and query

1. Create an Azure SQL logical server and a small Azure SQL **Database** in
   your isolated resource group using the
   [quickstart](https://learn.microsoft.com/en-us/azure/azure-sql/database/single-database-create-quickstart).
   Verify region, compute tier, minimum compute/storage and estimated charges;
   serverless auto-pause has eligibility rules and does not eliminate storage
   charges. Networking: allow only your own IP temporarily, not all Azure
   services or public internet. Remove the rule afterward.
2. Connect using Azure portal Query editor or a supported SQL client and an
   authorized identity. Do not put credentials in the repo or commands.
   Select the **database**, not `master`. Open and execute
   [`azure_sql.sql`](../sql/azure_sql.sql) in one session, in order.
   The temp tables are session-scoped; if disconnected, rerun from the start.
3. Expected totals: North 45.00 and South 32.00; January 3 returns O003 and
   O004. The script creates an index, enables statistics IO/time for the two
   selects, then disables them. Enable **actual execution plan** in a client
   that supports it; portal Query editor may not show the same plan UI.
   Compare scans/seeks, estimated versus actual rows, logical reads and time.
   A six-row table may still scan after indexing: there is no guaranteed
   performance improvement. Indexes add storage and write cost.

## 2. Query Store and waits

Run the final two DMV queries in the same file. Query Store should be enabled
in the database settings; data may take time to appear. The identity needs
the permissions required for the DMV on your Azure SQL version/tier (often
`VIEW DATABASE STATE` or `VIEW DATABASE PERFORMANCE STATE`); consult your
administrator rather than granting broad admin access. Inspect Query Store's
query/plan history and compare a regressed plan. Wait statistics are cumulative
since their reset; examine deltas and workload context, not a single wait as
proof of a bottleneck. Do not clear shared production wait stats.

## 3. Indexed and materialized views

An ordinary view stores a query definition. A SQL Server/Azure SQL **indexed
view** stores results via a unique clustered index; it needs deterministic
expressions, `SCHEMABINDING`, required `SET` options and has restrictions.
The optimizer's automatic use depends on platform and settings; maintenance
costs writes. Databricks SQL **materialized views** are managed separately
and refreshed according to their configuration; their refresh and cost model
is not the same as Azure SQL indexed views. Neither is automatically identical
to this lab's explicitly rebuilt gold table.

In an isolated Azure SQL database, this example creates persistent objects;
execute the whole block and the cleanup block in the same database:

```sql
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
CREATE TABLE dbo.LabViewSales (order_id int NOT NULL PRIMARY KEY, region varchar(10) NOT NULL, revenue decimal(10,2) NOT NULL);
INSERT dbo.LabViewSales VALUES (1,'North',10),(2,'North',15),(3,'South',8);
GO
CREATE VIEW dbo.LabRegionRevenue WITH SCHEMABINDING AS
SELECT region, COUNT_BIG(*) AS order_count, SUM(revenue) AS revenue
FROM dbo.LabViewSales GROUP BY region;
GO
CREATE UNIQUE CLUSTERED INDEX IX_LabRegionRevenue ON dbo.LabRegionRevenue(region);
SELECT * FROM dbo.LabRegionRevenue ORDER BY region;
GO
DROP VIEW dbo.LabRegionRevenue;
DROP TABLE dbo.LabViewSales;
```

`GO` is a client batch separator, not T-SQL; in a client that doesn't support
it, execute each block separated by `GO` individually. Expected: North 2/25
and South 1/8. If an error interrupts the exercise, run the two DROP statements
after verifying these names belong to this lab.

## 4. Partitioning and modelling

Partitioning divides one logical table/index by boundary values, often dates,
for maintenance and potential partition elimination. It does not automatically
make queries faster; date predicates, aligned indexes, constraints and data
distribution matter. Azure SQL Database uses the `PRIMARY` filegroup. Plan a
`RANGE RIGHT` monthly partition function: boundary `2025-02-01` sends February
1 into the right-hand partition. Sketch retention by switching/truncating
eligible partitions and explain alignment requirements before trying it.
Try this only in the isolated lab database, with a principal allowed to create
partition functions, schemes and tables. This creates persistent objects:

```sql
CREATE PARTITION FUNCTION LabMonthRange(date)
AS RANGE RIGHT FOR VALUES ('2025-02-01');
CREATE PARTITION SCHEME LabMonthScheme
AS PARTITION LabMonthRange ALL TO ([PRIMARY]);
CREATE TABLE dbo.LabPartitionSales (order_date date NOT NULL, revenue decimal(10,2) NOT NULL)
ON LabMonthScheme(order_date);
INSERT dbo.LabPartitionSales VALUES ('2025-01-31', 10), ('2025-02-01', 20);
SELECT order_date, $PARTITION.LabMonthRange(order_date) AS partition_number
FROM dbo.LabPartitionSales ORDER BY order_date;
```

Expected: January 31 is partition 1; February 1 is partition 2. Clean up
immediately, in this order:

```sql
DROP TABLE dbo.LabPartitionSales;
DROP PARTITION SCHEME LabMonthScheme;
DROP PARTITION FUNCTION LabMonthRange;
```

If interrupted, remove only the lab objects that were created. Do not change
a production table.

**Checkpoint:** explain fact grain, scan versus seek, write cost of an index,
why Query Store and waits are complementary, and the difference between
indexed and materialized views. Clean up all Azure resources.
References: [Query Store](https://learn.microsoft.com/en-us/azure/azure-sql/database/query-store-with-sql-database),
[indexed views](https://learn.microsoft.com/en-us/sql/relational-databases/views/create-indexed-views),
[Databricks materialized views](https://learn.microsoft.com/en-us/azure/databricks/ldp/dbsql/materialized).
