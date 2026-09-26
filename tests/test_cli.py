import io
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path

from cmo_retail.__main__ import parse_args


class ArgumentParsingTests(unittest.TestCase):
    def test_churn_parses_date_and_path_overrides(self):
        args = parse_args(
            [
                "churn",
                "--as-of",
                "2026-09-30",
                "--customers",
                "source/customers.csv",
                "--orders",
                "source/orders.csv",
                "--output",
                "reports/churn.csv",
            ]
        )
        self.assertEqual(args.as_of, date(2026, 9, 30))
        self.assertEqual(args.customers, Path("source/customers.csv"))
        self.assertEqual(args.orders, Path("source/orders.csv"))
        self.assertEqual(args.output, Path("reports/churn.csv"))

    def test_sales_uses_defaults(self):
        args = parse_args(["sales"])
        self.assertEqual(args.report, "sales")
        self.assertIsNone(args.as_of)
        self.assertEqual(args.customers, Path("data/customers.csv"))
        self.assertEqual(args.orders, Path("data/orders.csv"))

    def test_missing_or_invalid_as_of_is_rejected(self):
        for argv, message in (
            (["churn"], "--as-of is required"),
            (["churn", "--as-of", "not-a-date"], "invalid fromisoformat value"),
            (["sales", "--as-of", "2026-09-30"], "only valid for churn"),
        ):
            with self.subTest(argv=argv):
                stderr = io.StringIO()
                with redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
                    parse_args(argv)
                self.assertEqual(error.exception.code, 2)
                self.assertIn(message, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
