"""Deterministic customer churn and activation priorities."""

import csv
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


def customer_churn(
    customers: list[Customer], orders: list[Order], as_of: date
) -> list[dict[str, str]]:
    known = {customer.customer_id: customer for customer in customers}
    if len(known) != len(customers) or any(not key.strip() for key in known):
        raise ValueError("Customer IDs must be present and unique")
    if any(customer.joined_at > as_of for customer in customers):
        raise ValueError("Customers cannot join after the report date")
    history: dict[str, list[Order]] = {key: [] for key in known}
    seen = set()
    for order in orders:
        if not order.order_id.strip() or order.order_id in seen:
            raise ValueError("Order IDs must be present and unique")
        seen.add(order.order_id)
        if order.customer_id not in known:
            raise ValueError("Order references an unknown customer")
        if order.order_date < known[order.customer_id].joined_at:
            raise ValueError("Order predates customer joining")
        if (
            order.quantity <= 0
            or not order.unit_price.is_finite()
            or order.unit_price < 0
        ):
            raise ValueError("Invalid quantity or price")
        if order.order_date <= as_of:
            history[order.customer_id].append(order)

    rows = []
    for customer_id, customer in sorted(known.items()):
        purchases = history[customer_id]
        days = (
            (as_of - max(order.order_date for order in purchases)).days
            if purchases
            else None
        )
        recent = [order for order in purchases if (as_of - order.order_date).days < 90]
        if days is None:
            risk = "MEDIUM" if (as_of - customer.joined_at).days <= 30 else "HIGH"
        else:
            risk = "LOW" if days <= 30 else "MEDIUM" if days <= 90 else "HIGH"
        spend = sum(
            (order.quantity * order.unit_price for order in recent), Decimal("0")
        )
        rows.append(
            {
                "customer_id": customer_id,
                "days_since_last_purchase": "" if days is None else str(days),
                "purchases_last_90_days": str(len(recent)),
                "spend_last_90_days": f"{spend:.2f}",
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
