import csv
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from cmo_retail.churn import FIELDS, customer_churn, write_churn_report
from cmo_retail.models import Customer, Order

AS_OF = date(2026, 9, 30)


def customer(key="C1", age=200):
    return Customer(key, "private@example.test", AS_OF - timedelta(days=age))


def order(age, key="O1", customer_id="C1", price="0.10", quantity=3):
    return Order(
        key, customer_id, AS_OF - timedelta(days=age), "Books", quantity, Decimal(price)
    )


class ChurnTests(unittest.TestCase):
    def test_purchase_risk_boundaries(self):
        for age, expected in [
            (0, "LOW"),
            (30, "LOW"),
            (31, "MEDIUM"),
            (90, "MEDIUM"),
            (91, "HIGH"),
        ]:
            with self.subTest(age=age):
                row = customer_churn([customer()], [order(age)], AS_OF)[0]
                self.assertEqual(row["churn_risk"], expected)
                self.assertEqual(row["days_since_last_purchase"], str(age))

    def test_never_purchased_activation_boundaries(self):
        for age, expected in [(0, "MEDIUM"), (30, "MEDIUM"), (31, "HIGH")]:
            with self.subTest(age=age):
                row = customer_churn([customer(age=age)], [], AS_OF)[0]
                self.assertEqual(
                    row, dict(zip(FIELDS, ["C1", "", "0", "0.00", expected]))
                )

    def test_window_latest_purchase_and_exact_spend(self):
        orders = [order(age, str(age)) for age in [-1, 0, 89, 90, 91]]
        row = customer_churn([customer()], orders, AS_OF)[0]
        self.assertEqual(row["days_since_last_purchase"], "0")
        self.assertEqual(row["purchases_last_90_days"], "2")
        self.assertEqual(row["spend_last_90_days"], "0.60")
        self.assertEqual(
            customer_churn([customer()], [order(-1)], AS_OF)[0][
                "days_since_last_purchase"
            ],
            "",
        )

    def test_sorted_complete_and_repeatable(self):
        customers = [customer("C2"), customer()]
        orders = [order(2), order(1, "O2")]
        rows = customer_churn(customers, orders, AS_OF)
        self.assertEqual([row["customer_id"] for row in rows], ["C1", "C2"])
        self.assertEqual(rows, customer_churn(customers[::-1], orders[::-1], AS_OF))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "churn.csv"
            write_churn_report(path, rows)
            first = path.read_bytes()
            write_churn_report(path, rows)
            self.assertEqual(first, path.read_bytes())
            self.assertNotIn(b"private@example.test", first)
            with path.open(newline="") as source:
                self.assertEqual(csv.DictReader(source).fieldnames, FIELDS)
            write_churn_report(path, [])
            self.assertEqual(path.read_text().strip(), ",".join(FIELDS))
        self.assertEqual(customer_churn([], [], AS_OF), [])

    def test_invalid_data(self):
        cases = [
            ([customer(), customer()], []),
            ([customer(age=-1)], []),
            ([customer()], [order(201)]),
            ([customer()], [order(1, customer_id="missing")]),
            ([customer()], [order(1), order(2)]),
            ([customer()], [order(1, price="NaN")]),
            ([customer()], [order(1, price="-1")]),
            ([customer()], [order(1, quantity=0)]),
        ]
        for customers, orders in cases:
            with self.subTest(customers=customers, orders=orders):
                with self.assertRaises(ValueError):
                    customer_churn(customers, orders, AS_OF)

    def test_cli_requires_date_and_redacts_invalid_input(self):
        result = subprocess.run(
            [sys.executable, "-m", "cmo_retail", "churn"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --as-of", result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            customers = Path(directory) / "customers.csv"
            orders = Path(directory) / "orders.csv"
            output = Path(directory) / "report.csv"
            customers.write_text(
                "customer_id,email,joined_at\nC1,private@example.test,2026-01-01\n"
            )
            orders.write_text(
                "order_id,customer_id,order_date,category,quantity,unit_price\nO1,C1,2026-09-30,Books,3,0.10\n"
            )
            command = [
                sys.executable,
                "-m",
                "cmo_retail",
                "churn",
                "--as-of",
                AS_OF.isoformat(),
                "--customers",
                str(customers),
                "--orders",
                str(orders),
                "--output",
                str(output),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0.30,LOW", output.read_text())
            self.assertNotIn(
                "private@example.test",
                result.stdout + result.stderr + output.read_text(),
            )
            customers.write_text(
                "customer_id,email,joined_at\nC1,private@example.test,private@example.test\n"
            )
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("private@example.test", result.stdout + result.stderr)
