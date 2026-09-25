"""Existing business feature: daily category sales summary."""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from cmo_retail.models import Order


def daily_category_sales(orders: list[Order]) -> list[dict[str, str]]:
    grouped = defaultdict(
        lambda: {"orders": 0, "units": 0, "revenue": Decimal("0"), "customers": set()}
    )
    for order in orders:
        record = grouped[(order.order_date, order.category)]
        record["orders"] += 1
        record["units"] += order.quantity
        record["revenue"] += order.quantity * order.unit_price
        record["customers"].add(order.customer_id)
    return [
        {
            "order_date": day.isoformat(),
            "category": category,
            "orders_count": str(grouped[(day, category)]["orders"]),
            "units_sold": str(grouped[(day, category)]["units"]),
            "gross_revenue": f"{grouped[(day, category)]['revenue']:.2f}",
            "unique_customers": str(len(grouped[(day, category)]["customers"])),
        }
        for day, category in sorted(grouped)
    ]


def write_sales_report(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(
            destination,
            fieldnames=[
                "order_date",
                "category",
                "orders_count",
                "units_sold",
                "gross_revenue",
                "unique_customers",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
