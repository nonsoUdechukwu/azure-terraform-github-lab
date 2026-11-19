# Databricks notebook source
# MAGIC %md
# MAGIC # Retail medallion pipeline
# MAGIC Upload the three CSV files to a Unity Catalog volume first. See lesson 02.
# MAGIC Run all cells twice to verify idempotency. Only synthetic data is used.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Existing catalog")
dbutils.widgets.text("schema", "retail_lab", "Lab schema")
dbutils.widgets.text("volume_path", "", "Volume path containing CSV files")

import re
from pyspark.sql import Window, functions as F
from pyspark.sql.types import StringType, StructField, StructType
from delta.tables import DeltaTable

catalog = dbutils.widgets.get("catalog").strip()
schema = dbutils.widgets.get("schema").strip()
volume = dbutils.widgets.get("volume_path").strip().rstrip("/")
if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", x) for x in (catalog, schema)):
    raise ValueError("Use simple catalog and schema identifiers (letters, digits, underscore).")
if not volume.startswith("/Volumes/"):
    raise ValueError("Set volume_path to your Unity Catalog volume, e.g. /Volumes/workspace/retail_lab/files")
namespace = f"`{catalog}`.`{schema}`"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {namespace}")

order_columns = ["event_id", "order_id", "customer_id", "product_id", "order_date", "quantity", "unit_price", "updated_at"]
def read_strings(filename, columns):
    schema_def = StructType([StructField(name, StringType(), True) for name in columns])
    return (spark.read.option("header", True).option("enforceSchema", False)
            .schema(schema_def).csv(f"{volume}/{filename}"))

orders = read_strings("orders.csv", order_columns)
customers = read_strings("customers.csv", ["customer_id", "customer_name", "region"])
products = read_strings("products.csv", ["product_id", "product_name", "category"])
for frame, key in [(orders, "event_id"), (customers, "customer_id"), (products, "product_id")]:
    if frame.filter(F.col(key).isNull() | (F.trim(F.col(key)) == "")).limit(1).count():
        raise ValueError(f"{key} must be present")
    if frame.groupBy(key).count().filter("count > 1").limit(1).count():
        raise ValueError(f"{key} must be unique in the input")

# COMMAND ----------

# Snapshot dimensions; merge raw events by their stable event_id.
customers.write.format("delta").mode("overwrite").saveAsTable(f"{namespace}.dim_customer")
products.write.format("delta").mode("overwrite").saveAsTable(f"{namespace}.dim_product")
orders.write.format("delta").mode("ignore").saveAsTable(f"{namespace}.bronze_orders")
DeltaTable.forName(spark, f"{namespace}.bronze_orders").alias("target").merge(
    orders.alias("source"), "target.event_id = source.event_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
bronze = spark.table(f"{namespace}.bronze_orders")

# COMMAND ----------

# Parse without aborting on bad input; retain invalid rows separately.
parsed = (bronze
    .withColumn("quantity_int", F.expr("try_cast(quantity AS INT)"))
    .withColumn("price_decimal", F.expr("try_cast(unit_price AS DECIMAL(12,2))"))
    .withColumn("date_value", F.expr("try_cast(order_date AS DATE)"))
    .withColumn("timestamp_value", F.expr("try_cast(updated_at AS TIMESTAMP)"))
    .join(customers.select("customer_id").withColumn("known_customer", F.lit(True)), "customer_id", "left")
    .join(products.select("product_id").withColumn("known_product", F.lit(True)), "product_id", "left"))
valid = (
    F.col("order_id").isNotNull() & (F.length(F.col("order_id")) > 0) &
    F.col("known_customer").isNotNull() & F.col("known_product").isNotNull() &
    F.col("order_date").rlike(r"^\d{4}-\d{2}-\d{2}$") & F.col("date_value").isNotNull() &
    F.col("updated_at").rlike(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$") & F.col("timestamp_value").isNotNull() &
    F.col("quantity").rlike(r"^\+?\d+$") & (F.col("quantity_int") > 0) &
    F.col("unit_price").rlike(r"^\d+(\.\d{1,2})?$") & F.col("price_decimal").isNotNull()
)
parsed = parsed.withColumn("is_valid", F.coalesce(valid, F.lit(False)))
(parsed.filter("NOT is_valid").select(*order_columns)
 .write.format("delta").mode("overwrite").saveAsTable(f"{namespace}.quarantine_orders"))
rank = Window.partitionBy("order_id").orderBy(F.col("timestamp_value").desc(), F.col("event_id").desc())
silver = (parsed.filter("is_valid").withColumn("rank", F.row_number().over(rank)).filter("rank = 1")
    .select("order_id", "event_id", "customer_id", "product_id",
            F.col("date_value").alias("order_date"), F.col("quantity_int").alias("quantity"),
            F.col("price_decimal").alias("unit_price"), F.col("timestamp_value").alias("updated_at")))
silver.write.format("delta").mode("ignore").saveAsTable(f"{namespace}.silver_orders")
DeltaTable.forName(spark, f"{namespace}.silver_orders").alias("target").merge(
    silver.alias("source"), "target.order_id = source.order_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().whenNotMatchedBySourceDelete().execute()

# COMMAND ----------

fact = spark.table(f"{namespace}.silver_orders")
gold = (fact.join(customers, "customer_id").join(products, "product_id")
    .groupBy("order_date", "region", "category")
    .agg(F.count("*").alias("orders"),
         F.sum(F.col("quantity") * F.col("unit_price")).alias("revenue")))
gold.write.format("delta").mode("overwrite").saveAsTable(f"{namespace}.gold_daily")
print("bronze, silver, quarantine, gold groups:",
      *[spark.table(f"{namespace}.{table}").count() for table in
        ("bronze_orders", "silver_orders", "quarantine_orders", "gold_daily")])
print("total revenue:", spark.table(f"{namespace}.gold_daily").agg(F.sum("revenue")).first()[0])
display(spark.table(f"{namespace}.gold_daily").orderBy("order_date", "region", "category"))

# COMMAND ----------

# Parquet is a file format; unlike a Delta table, this folder has no Delta log.
parquet_path = f"{volume}/parquet_orders"
fact.write.mode("overwrite").parquet(parquet_path)
print("parquet rows:", spark.read.parquet(parquet_path).count())
display(spark.sql(f"DESCRIBE HISTORY {namespace}.bronze_orders"))
