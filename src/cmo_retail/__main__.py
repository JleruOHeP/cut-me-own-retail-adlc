"""Command line entry point for retail reports."""

import argparse
from datetime import date
from pathlib import Path

from cmo_retail.churn import customer_churn, write_churn_report
from cmo_retail.io import load_customers, load_orders
from cmo_retail.sales import daily_category_sales, write_sales_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Cut-Me-Own retail reports")
    parser.add_argument("report", choices=["sales", "churn"])
    parser.add_argument(
        "--as-of", type=date.fromisoformat, help="Report date (YYYY-MM-DD)"
    )
    parser.add_argument("--customers", type=Path, default=Path("data/customers.csv"))
    parser.add_argument("--orders", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.report == "churn" and args.as_of is None:
        parser.error("churn requires --as-of YYYY-MM-DD")
    output = args.output or Path(
        "output/daily_sales.csv"
        if args.report == "sales"
        else "output/customer_churn.csv"
    )

    try:
        customers = load_customers(args.customers)
        orders = load_orders(args.orders, customers)
        if args.report == "churn":
            rows = customer_churn(customers, orders, args.as_of)
            write_churn_report(output, rows)
        else:
            rows = daily_category_sales(orders)
            write_sales_report(output, rows)
    except ValueError:
        parser.error("Invalid input data; check IDs, dates, quantities and prices")
    print(f"Wrote {len(rows)} {args.report} rows to {output}")


if __name__ == "__main__":
    main()
