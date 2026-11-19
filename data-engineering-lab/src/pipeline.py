#!/usr/bin/env python3
"""A small SQLite medallion pipeline for offline practice."""

import argparse
import csv
import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER_FIELDS = (
    "event_id", "order_id", "customer_id", "product_id", "order_date",
    "quantity", "unit_price", "updated_at",
)


def read_csv(path, expected):
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != list(expected):
            raise ValueError(f"{path}: expected columns {', '.join(expected)}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"{path}: malformed CSV row")
    return rows


def validate(row, customers, products):
    try:
        if not row["order_id"] or row["customer_id"] not in customers or row["product_id"] not in products:
            return "missing order or unknown customer/product"
        if date.fromisoformat(row["order_date"]).isoformat() != row["order_date"]:
            return "invalid date"
        if datetime.strptime(row["updated_at"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S") != row["updated_at"]:
            return "invalid timestamp"
        quantity = int(row["quantity"])
        price = Decimal(row["unit_price"])
        if quantity <= 0 or not price.is_finite() or price < 0 or price * 100 != (price * 100).to_integral_value():
            return "invalid quantity or price"
        return None
    except (ValueError, InvalidOperation):
        return "invalid date, timestamp, quantity or price"


def run(db_path, data_dir):
    customers = read_csv(data_dir / "customers.csv", ("customer_id", "customer_name", "region"))
    products = read_csv(data_dir / "products.csv", ("product_id", "product_name", "category"))
    orders = read_csv(data_dir / "orders.csv", ORDER_FIELDS)
    for rows, key in ((customers, "customer_id"), (products, "product_id"), (orders, "event_id")):
        ids = [row[key] for row in rows]
        if not all(ids) or len(set(ids)) != len(ids):
            raise ValueError(f"{key} must be nonempty and unique in each input")

    with sqlite3.connect(db_path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS bronze (
              event_id TEXT PRIMARY KEY, order_id TEXT, customer_id TEXT,
              product_id TEXT, order_date TEXT, quantity TEXT, unit_price TEXT, updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS dim_customer (
              customer_id TEXT PRIMARY KEY, customer_name TEXT, region TEXT
            );
            CREATE TABLE IF NOT EXISTS dim_product (
              product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT
            );
            CREATE TABLE IF NOT EXISTS quarantine (event_id TEXT PRIMARY KEY, reason TEXT);
            CREATE TABLE IF NOT EXISTS silver (
              order_id TEXT PRIMARY KEY, event_id TEXT, customer_id TEXT, product_id TEXT,
              order_date TEXT, quantity INTEGER, unit_price_cents INTEGER, updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS gold_daily (
              order_date TEXT, region TEXT, category TEXT, orders INTEGER, revenue_cents INTEGER,
              PRIMARY KEY (order_date, region, category)
            );
        """)
        # Dimensions are snapshots; bronze retains events absent from later input batches.
        with db:
            db.execute("DELETE FROM dim_customer")
            db.execute("DELETE FROM dim_product")
            db.executemany("INSERT INTO dim_customer VALUES (:customer_id, :customer_name, :region)", customers)
            db.executemany("INSERT INTO dim_product VALUES (:product_id, :product_name, :category)", products)
            db.executemany("""
              INSERT INTO bronze VALUES (:event_id, :order_id, :customer_id, :product_id,
                :order_date, :quantity, :unit_price, :updated_at)
              ON CONFLICT(event_id) DO UPDATE SET order_id=excluded.order_id,
                customer_id=excluded.customer_id, product_id=excluded.product_id,
                order_date=excluded.order_date, quantity=excluded.quantity,
                unit_price=excluded.unit_price, updated_at=excluded.updated_at
            """, orders)
            db.execute("DELETE FROM quarantine")
            db.execute("DELETE FROM silver")
            db.execute("DELETE FROM gold_daily")
            db.row_factory = sqlite3.Row
            valid = []
            for record in db.execute("SELECT * FROM bronze").fetchall():
                row = dict(record)
                reason = validate(row, {r["customer_id"] for r in customers}, {r["product_id"] for r in products})
                if reason:
                    db.execute("INSERT INTO quarantine VALUES (?, ?)", (row["event_id"], reason))
                else:
                    valid.append(row)
            for row in sorted(valid, key=lambda r: (r["updated_at"], r["event_id"])):
                db.execute("""
                  INSERT INTO silver VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                  ON CONFLICT(order_id) DO UPDATE SET event_id=excluded.event_id,
                    customer_id=excluded.customer_id, product_id=excluded.product_id,
                    order_date=excluded.order_date, quantity=excluded.quantity,
                    unit_price_cents=excluded.unit_price_cents, updated_at=excluded.updated_at
                """, (row["order_id"], row["event_id"], row["customer_id"], row["product_id"],
                      row["order_date"], int(row["quantity"]), int(Decimal(row["unit_price"]) * 100),
                      row["updated_at"]))
            db.execute("""
              INSERT INTO gold_daily
              SELECT s.order_date, c.region, p.category, COUNT(*),
                     SUM(s.quantity * s.unit_price_cents)
              FROM silver s JOIN dim_customer c ON s.customer_id=c.customer_id
              JOIN dim_product p ON s.product_id=p.product_id
              GROUP BY s.order_date, c.region, p.category
            """)
        return tuple(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                     for table in ("bronze", "silver", "quarantine", "gold_daily"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "retail.db")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    counts = run(args.db, args.data)
    print("bronze=%d silver=%d quarantine=%d gold_groups=%d" % counts)
