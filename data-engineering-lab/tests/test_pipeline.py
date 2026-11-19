import csv
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipeline import run


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "data", self.root / "data")
        self.db = self.root / "retail.db"

    def tearDown(self):
        self.tmp.cleanup()

    def query(self, sql):
        with sqlite3.connect(self.db) as db:
            return db.execute(sql).fetchall()

    def test_baseline_and_rerun_are_idempotent(self):
        self.assertEqual(run(self.db, self.root / "data"), (9, 6, 2, 6))
        before = self.query("SELECT * FROM gold_daily ORDER BY 1, 2, 3")
        self.assertEqual(run(self.db, self.root / "data"), (9, 6, 2, 6))
        self.assertEqual(before, self.query("SELECT * FROM gold_daily ORDER BY 1, 2, 3"))
        self.assertEqual(self.query("SELECT SUM(revenue_cents) FROM gold_daily"), [(7700,)])
        self.assertEqual(self.query("SELECT event_id, quantity FROM silver WHERE order_id='O002'"), [("E007", 2)])
        self.assertEqual(self.query("SELECT event_id FROM quarantine ORDER BY event_id"), [("E008",), ("E009",)])

    def test_new_and_invalid_event(self):
        run(self.db, self.root / "data")
        with (self.root / "data" / "orders.csv").open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["E010", "O001", "C001", "P001", "2025-01-02", "3", "5.00", "2025-01-06T10:00:00"])
            writer.writerow(["E011", "O009", "C001", "P001", "2025-01-06", "1", "1.001", "2025-01-06T11:00:00"])
        self.assertEqual(run(self.db, self.root / "data"), (11, 6, 3, 6))
        self.assertEqual(self.query("SELECT SUM(revenue_cents) FROM gold_daily"), [(8200,)])
        self.assertEqual(self.query("SELECT event_id FROM silver WHERE order_id='O001'"), [("E010",)])

    def test_rejects_duplicate_event_ids(self):
        path = self.root / "data" / "orders.csv"
        with path.open("a", encoding="utf-8") as file:
            file.write("E001,O999,C001,P001,2025-01-02,1,5.00,2025-01-02T10:00:00\n")
        with self.assertRaisesRegex(ValueError, "event_id"):
            run(self.db, self.root / "data")


if __name__ == "__main__":
    unittest.main()
