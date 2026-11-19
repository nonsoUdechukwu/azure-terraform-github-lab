# 01: Python, SQL and a star schema

**Goal:** explain the data's grain, run a pipeline and answer business questions.
Work from `data-engineering-lab/`. Time: 3–5 hours.

## 1. Explore Python and the input

In a terminal run:

```bash
python3 - <<'PY'
import csv
from decimal import Decimal
with open("data/orders.csv", newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
print("events:", len(rows))
print("first order:", rows[0]["order_id"])
print("first revenue:", int(rows[0]["quantity"]) * Decimal(rows[0]["unit_price"]))
PY
```

Expected: `events: 9`, `first order: O001`, `first revenue: 10.00`.
`rows` is a list of dictionaries. Access a field by key; `int` converts text to
an integer; `Decimal` avoids binary floating-point money errors. Change the
index to `1`, then write a loop printing every order ID. Restore nothing: this
snippet does not edit data. Learn [Python basics](https://docs.python.org/3/tutorial/).

## 2. Run and inspect the pipeline

```bash
python3 src/pipeline.py
python3 src/pipeline.py
python3 -m unittest discover -s tests -v
```

Both runs print `bronze=9 silver=6 quarantine=2 gold_groups=6`. Tests should
pass. Read `src/pipeline.py`: `read_csv` loads dictionaries, `validate` returns
a reason or `None`, and `run` uses a transaction, SQL inserts and a loop. The
database is `retail.db`; delete only this generated file to reset.

## 3. Query facts and dimensions

Run this exact command; it uses Python's built-in SQLite rather than requiring
the `sqlite3` command-line tool:

```bash
python3 - <<'PY'
import sqlite3
db = sqlite3.connect("retail.db")
queries = [
    "SELECT event_id, reason FROM quarantine ORDER BY event_id",
    "SELECT order_id, event_id, quantity FROM silver ORDER BY order_id",
    "SELECT region, SUM(revenue_cents)/100.0 FROM gold_daily GROUP BY region ORDER BY region",
    "SELECT SUM(revenue_cents)/100.0 FROM gold_daily",
]
for query in queries:
    print(query)
    for row in db.execute(query):
        print(row)
db.close()
PY
```

Expected quarantine IDs: `E008`, `E009`; `O002` uses `E007`, quantity 2.
North revenue is 45.0, South 32.0, total 77.0. Open
[`analysis.sql`](../sql/analysis.sql) and run its three statements in this
reusable runner:

```bash
python3 - <<'PY'
import sqlite3
db = sqlite3.connect("retail.db")
statement = ""
for line in open("sql/analysis.sql", encoding="utf-8"):
    statement += line
    if sqlite3.complete_statement(statement):
        for row in db.execute(statement):
            print(row)
        statement = ""
db.close()
PY
```

An inner **join** combines facts with matching dimensions; `GROUP BY` reduces
rows to groups; `ROW_NUMBER()` ranks within each region without collapsing
orders. The sample intentionally has no valid unmatched dimensions.

## 4. Model and check

Draw a star: `silver` is a fact with grain **one current valid order**;
`dim_customer` and `dim_product` describe it. `gold_daily` has a different
grain: **one date × region × category**. A customer dimension is not a fact:
it provides descriptive context. A date dimension could add month/holiday
attributes; it is not implemented here. Revenue is additive at these grains.
Explain why joining events directly to dimensions before selecting the latest
order double-counts O002. Answer: both E002 and E007 would contribute.

Experiment in a copy of the input, not the tracked CSV:

```bash
mkdir -p /tmp/retail-lab-input
cp data/*.csv /tmp/retail-lab-input/
python3 src/pipeline.py --data /tmp/retail-lab-input --db /tmp/retail-lab-experiment.db
```

Append a unique event with a later timestamp for an existing order to the copy
and rerun; inspect the changed order and total using the query pattern above.
Do not edit event IDs to be duplicates in one CSV: ingestion rejects them.
For further SQL practice see [SQL concepts](https://learn.microsoft.com/en-us/training/modules/query-relational-data/).

**Checkpoint:** state the two grains, why E007 wins, and why rerunning gives
the same six orders. If a command fails, check your directory (`pwd`) and Python
version. If old output differs, use a fresh database path; bronze deliberately
retains old events even if they disappear from an input file.
