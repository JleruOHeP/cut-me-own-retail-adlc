"""Command line entry point for retail reports."""

import argparse
from datetime import date
from pathlib import Path

from cmo_retail.churn import customer_churn_risk, write_churn_report
from cmo_retail.io import load_customers, load_orders
from cmo_retail.sales import daily_category_sales, write_sales_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cut-Me-Own retail reports")
    parser.add_argument("report", choices=["sales", "churn"])
    parser.add_argument("--customers", type=Path, default=Path("data/customers.csv"))
    parser.add_argument("--orders", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--as-of", type=date.fromisoformat, help="Report date (YYYY-MM-DD)"
    )
    args = parser.parse_args(argv)
    if args.report == "sales" and args.as_of is not None:
        parser.error("--as-of is only valid for churn")
    if args.report == "churn" and args.as_of is None:
        parser.error("--as-of is required for churn")
    return args


def main() -> None:
    args = parse_args()

    customers = load_customers(args.customers)
    orders = load_orders(args.orders, customers)
    if args.report == "sales":
        output = args.output or Path("output/daily_sales.csv")
        rows = daily_category_sales(orders)
        write_sales_report(output, rows)
    else:
        output = args.output or Path("output/customer_churn_risk.csv")
        try:
            rows = customer_churn_risk(customers, orders, args.as_of)
        except ValueError as error:
            raise SystemExit(str(error)) from None
        write_churn_report(output, rows)
    print(f"Wrote {len(rows)} {args.report} rows to {output}")


if __name__ == "__main__":
    main()
