"""Deterministic customer churn and activation priority report."""

import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from cmo_retail.models import Customer, Order

FIELDS = [
    "customer_id",
    "days_since_last_purchase",
    "purchases_last_90_days",
    "spend_last_90_days",
    "churn_risk",
]


def customer_churn_risk(
    customers: list[Customer], orders: list[Order], as_of: date
) -> list[dict[str, str]]:
    """Build one row per joined customer using purchases through the report date."""
    by_id = {customer.customer_id: customer for customer in customers}
    if len(by_id) != len(customers):
        raise ValueError("Customer IDs must be unique")
    joined_customers = [
        customer for customer in customers if customer.joined_at <= as_of
    ]

    last_purchase = {}
    purchase_count = defaultdict(int)
    spend = defaultdict(lambda: Decimal("0"))
    for order in orders:
        customer = by_id.get(order.customer_id)
        if customer is None:
            raise ValueError("Order references an unknown customer")
        if customer.joined_at > as_of:
            continue
        if order.order_date < customer.joined_at:
            raise ValueError("Order date cannot precede customer join date")
        if order.order_date > as_of:
            continue
        previous = last_purchase.get(order.customer_id)
        if previous is None or order.order_date > previous:
            last_purchase[order.customer_id] = order.order_date
        if (as_of - order.order_date).days <= 89:
            purchase_count[order.customer_id] += 1
            spend[order.customer_id] += order.quantity * order.unit_price

    rows = []
    for customer in sorted(joined_customers, key=lambda item: item.customer_id):
        last = last_purchase.get(customer.customer_id)
        if last is None:
            days_since = ""
            risk = "MEDIUM" if (as_of - customer.joined_at).days <= 30 else "HIGH"
        else:
            days = (as_of - last).days
            days_since = str(days)
            risk = "LOW" if days <= 30 else "MEDIUM" if days <= 90 else "HIGH"
        rows.append(
            {
                "customer_id": customer.customer_id,
                "days_since_last_purchase": days_since,
                "purchases_last_90_days": str(purchase_count[customer.customer_id]),
                "spend_last_90_days": f"{spend[customer.customer_id]:.2f}",
                "churn_risk": risk,
            }
        )
    return rows


def write_churn_report(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
