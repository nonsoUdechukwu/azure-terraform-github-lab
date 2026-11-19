-- Optional Azure SQL Database exercise. Run in a new query window.
-- Temp tables avoid leaving permanent objects behind; reconnecting removes them.
CREATE TABLE #customer (customer_id varchar(4) PRIMARY KEY, region varchar(10));
CREATE TABLE #sales (order_id varchar(4) PRIMARY KEY, customer_id varchar(4),
                     order_date date, revenue decimal(10,2));
INSERT INTO #customer VALUES ('C001','North'),('C002','South'),('C003','North');
INSERT INTO #sales VALUES
  ('O001','C001','2025-01-02',10),('O002','C002','2025-01-02',8),
  ('O003','C001','2025-01-03',12),('O004','C003','2025-01-03',15),
  ('O005','C002','2025-01-04',24),('O006','C003','2025-01-04',8);

SELECT c.region, SUM(s.revenue) AS revenue
FROM #sales AS s JOIN #customer AS c ON c.customer_id = s.customer_id
GROUP BY c.region;
-- North = 45.00; South = 32.00

SET STATISTICS IO ON;
SET STATISTICS TIME ON;
SELECT order_id, revenue FROM #sales WHERE order_date = '2025-01-03';
CREATE INDEX IX_sales_date ON #sales(order_date) INCLUDE(revenue);
SELECT order_id, revenue FROM #sales WHERE order_date = '2025-01-03';
SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
-- Tiny tables may scan even after indexing; compare the actual plans and IO,
-- not a promised speedup.

-- Query Store must be enabled and permissions granted. In Azure SQL Database,
-- database-scoped wait stats are available through this DMV, subject to permissions.
SELECT TOP (10) wait_type, wait_time_ms, waiting_tasks_count
FROM sys.dm_db_wait_stats ORDER BY wait_time_ms DESC;
SELECT TOP (10) q.query_id, SUM(rs.count_executions) AS executions,
  MAX(rs.last_execution_time) AS last_execution
FROM sys.query_store_query AS q
JOIN sys.query_store_plan AS p ON p.query_id = q.query_id
JOIN sys.query_store_runtime_stats AS rs ON rs.plan_id = p.plan_id
GROUP BY q.query_id ORDER BY last_execution DESC;
