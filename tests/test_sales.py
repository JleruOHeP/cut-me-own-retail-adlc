import csv
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from cmo_retail.io import load_customers, load_orders
from cmo_retail.models import Customer, Order
from cmo_retail.sales import daily_category_sales, write_sales_report


class SalesTests(unittest.TestCase):
    def test_daily_sales_groups_and_sorts(self):
        orders = [
            Order("O2", "C1", date(2026, 7, 1), "Books", 2, Decimal("12.50")),
            Order("O1", "C1", date(2026, 7, 1), "Books", 1, Decimal("10.00")),
            Order("O3", "C2", date(2026, 6, 30), "Garden", 1, Decimal("8")),
        ]
        result = daily_category_sales(orders)
        self.assertEqual(result[0]["order_date"], "2026-06-30")
        self.assertEqual(result[1]["gross_revenue"], "35.00")
        self.assertEqual(result[1]["unique_customers"], "1")
        self.assertEqual(result[1]["orders_count"], "2")

    def test_report_writes_header_even_when_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports" / "sales.csv"
            write_sales_report(path, [])
            with path.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(rows, [])
            self.assertIn("gross_revenue", path.read_text(encoding="utf-8"))

    def test_csv_reader_rejects_unknown_customer(self):
        customers = [Customer("C1", "private@example.test", date(2026, 1, 1))]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.csv"
            path.write_text(
                "order_id,customer_id,order_date,category,quantity,unit_price\n"
                "O1,C9,2026-09-01,Books,1,2.00\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Unknown customer ID"):
                load_orders(path, customers)

    def test_csv_reader_rejects_duplicate_customer_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "customers.csv"
            path.write_text(
                "customer_id,email,joined_at\n"
                "C1,a@example.test,2026-01-01\n"
                "C1,b@example.test,2026-01-02\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique"):
                load_customers(path)


if __name__ == "__main__":
    unittest.main()
