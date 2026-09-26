import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from cmo_retail.__main__ import main
from cmo_retail.churn import FIELDS, customer_churn_risk, write_churn_report
from cmo_retail.models import Customer, Order


class ChurnTests(unittest.TestCase):
    def setUp(self):
        self.as_of = date(2026, 9, 30)

    def customer(self, customer_id, joined_days_ago=200):
        return Customer(
            customer_id,
            "private@example.test",
            self.as_of - timedelta(days=joined_days_ago),
        )

    def order(self, order_id, customer_id, days_ago, quantity=1, price="2.50"):
        return Order(
            order_id,
            customer_id,
            self.as_of - timedelta(days=days_ago),
            "Books",
            quantity,
            Decimal(price),
        )

    def test_purchase_risk_boundaries_and_90_day_window(self):
        customers = [self.customer(f"C{days}") for days in (0, 30, 31, 89, 90, 91)]
        orders = [
            self.order(f"O{days}", f"C{days}", days, quantity=2)
            for days in (0, 30, 31, 89, 90, 91)
        ]
        by_id = {
            row["customer_id"]: row
            for row in customer_churn_risk(customers, orders, self.as_of)
        }
        for days, risk in (
            (0, "LOW"),
            (30, "LOW"),
            (31, "MEDIUM"),
            (89, "MEDIUM"),
            (90, "MEDIUM"),
            (91, "HIGH"),
        ):
            with self.subTest(days=days):
                row = by_id[f"C{days}"]
                self.assertEqual(row["days_since_last_purchase"], str(days))
                self.assertEqual(row["churn_risk"], risk)
                self.assertEqual(
                    row["purchases_last_90_days"], "1" if days < 90 else "0"
                )
                self.assertEqual(
                    row["spend_last_90_days"], "5.00" if days < 90 else "0.00"
                )

    def test_never_purchased_join_boundaries_and_future_order(self):
        customers = [
            self.customer("C31", 31),
            self.customer("C0", 0),
            self.customer("C30", 30),
        ]
        orders = [self.order("OFUTURE", "C31", -1)]
        rows = customer_churn_risk(customers, orders, self.as_of)
        self.assertEqual([row["customer_id"] for row in rows], ["C0", "C30", "C31"])
        self.assertEqual(
            [row["churn_risk"] for row in rows], ["MEDIUM", "MEDIUM", "HIGH"]
        )
        for row in rows:
            self.assertEqual(row["days_since_last_purchase"], "")
            self.assertEqual(row["purchases_last_90_days"], "0")
            self.assertEqual(row["spend_last_90_days"], "0.00")
            self.assertEqual(list(row), FIELDS)
            self.assertNotIn("private@example.test", str(row))

    def test_multiple_orders_sum_spend_and_ignore_future(self):
        customers = [self.customer("C1")]
        orders = [
            self.order("O1", "C1", 15, quantity=2, price="1.25"),
            self.order("O2", "C1", 2, quantity=3, price="0.10"),
            self.order("O3", "C1", -2, price="100"),
        ]
        row = customer_churn_risk(customers, orders, self.as_of)[0]
        self.assertEqual(row["days_since_last_purchase"], "2")
        self.assertEqual(row["purchases_last_90_days"], "2")
        self.assertEqual(row["spend_last_90_days"], "2.80")

    def test_future_joiners_are_excluded_without_blocking_valid_customers(self):
        customers = [self.customer("CFUTURE", -1), self.customer("CJOINED", 20)]
        orders = [
            self.order("OFUTURE", "CFUTURE", -1),
            self.order("OJOINED", "CJOINED", 5),
        ]
        rows = customer_churn_risk(customers, orders, self.as_of)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["customer_id"], "CJOINED")
        self.assertEqual(rows[0]["days_since_last_purchase"], "5")
        self.assertEqual(rows[0]["purchases_last_90_days"], "1")
        self.assertEqual(rows[0]["spend_last_90_days"], "2.50")

    def test_invalid_customer_and_order_dates(self):
        with self.assertRaisesRegex(ValueError, "join date"):
            customer_churn_risk(
                [self.customer("C1", 10)], [self.order("O1", "C1", 11)], self.as_of
            )
        with self.assertRaisesRegex(ValueError, "unknown customer"):
            customer_churn_risk(
                [self.customer("C1")], [self.order("O1", "C2", 1)], self.as_of
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            customer_churn_risk(
                [self.customer("C1"), self.customer("C1")], [], self.as_of
            )

    def test_writer_header_and_no_pii(self):
        rows = customer_churn_risk([self.customer("C1")], [], self.as_of)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports" / "churn.csv"
            write_churn_report(path, rows)
            contents = path.read_text(encoding="utf-8")
            self.assertNotIn("private@example.test", contents)
            with path.open(newline="", encoding="utf-8") as source:
                reader = csv.DictReader(source)
                self.assertEqual(reader.fieldnames, FIELDS)
                self.assertEqual(list(reader), rows)
            write_churn_report(path, [])
            self.assertEqual(path.read_text(encoding="utf-8").strip(), ",".join(FIELDS))

    def test_cli_same_inputs_and_date_produce_identical_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            customers = root / "customers.csv"
            orders = root / "orders.csv"
            output = root / "churn.csv"
            customers.write_text(
                "customer_id,email,joined_at\nC2,private@example.test,2026-01-01\n"
                "C1,other@example.test,2026-09-01\n",
                encoding="utf-8",
            )
            orders.write_text(
                "order_id,customer_id,order_date,category,quantity,unit_price\n"
                "O1,C2,2026-09-01,Books,2,3.25\n",
                encoding="utf-8",
            )
            argv = [
                "cmo_retail",
                "churn",
                "--as-of",
                "2026-09-30",
                "--customers",
                str(customers),
                "--orders",
                str(orders),
                "--output",
                str(output),
            ]
            messages = io.StringIO()
            with patch("sys.argv", argv), redirect_stdout(messages):
                main()
                first = output.read_bytes()
                main()
            self.assertEqual(output.read_bytes(), first)
            self.assertNotIn("private@example.test", messages.getvalue())
            self.assertNotIn("private@example.test", first.decode("utf-8"))
            self.assertNotIn("other@example.test", first.decode("utf-8"))

    def test_cli_writes_report_with_future_joiner_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            customers = root / "customers.csv"
            orders = root / "orders.csv"
            output = root / "churn.csv"
            customers.write_text(
                "customer_id,email,joined_at\n"
                "C1,private@example.test,2026-09-01\n"
                "C2,future@example.test,2026-10-01\n",
                encoding="utf-8",
            )
            orders.write_text(
                "order_id,customer_id,order_date,category,quantity,unit_price\n"
                "O1,C1,2026-09-15,Books,1,2.50\n"
                "O2,C2,2026-10-01,Books,1,9.00\n",
                encoding="utf-8",
            )
            argv = [
                "cmo_retail",
                "churn",
                "--as-of",
                "2026-09-30",
                "--customers",
                str(customers),
                "--orders",
                str(orders),
                "--output",
                str(output),
            ]
            with patch("sys.argv", argv), redirect_stdout(io.StringIO()):
                main()
            with output.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["customer_id"], "C1")


if __name__ == "__main__":
    unittest.main()
