"""Command line entry point for the existing sales report."""

import argparse
from pathlib import Path

from cmo_retail.io import load_customers, load_orders
from cmo_retail.sales import daily_category_sales, write_sales_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Cut-Me-Own retail reports")
    parser.add_argument("report", choices=["sales"])
    parser.add_argument("--customers", type=Path, default=Path("data/customers.csv"))
    parser.add_argument("--orders", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path, default=Path("output/daily_sales.csv"))
    args = parser.parse_args()

    customers = load_customers(args.customers)
    orders = load_orders(args.orders, customers)
    rows = daily_category_sales(orders)
    write_sales_report(args.output, rows)
    print(f"Wrote {len(rows)} sales rows to {args.output}")


if __name__ == "__main__":
    main()
