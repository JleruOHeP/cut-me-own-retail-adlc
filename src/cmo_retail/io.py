"""Strict CSV input parsing. Source email is available but never logged."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cmo_retail.models import Customer, Order


def _rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"Invalid columns in {path.name}")
        return list(reader)


def load_customers(path: Path) -> list[Customer]:
    result = []
    seen = set()
    for row in _rows(path, {"customer_id", "email", "joined_at"}):
        customer_id = row["customer_id"].strip()
        if not customer_id or customer_id in seen:
            raise ValueError("Customer IDs must be present and unique")
        seen.add(customer_id)
        result.append(
            Customer(
                customer_id, row["email"].strip(), date.fromisoformat(row["joined_at"])
            )
        )
    return result


def load_orders(path: Path, customers: list[Customer]) -> list[Order]:
    known = {customer.customer_id for customer in customers}
    seen = set()
    result = []
    fields = {
        "order_id",
        "customer_id",
        "order_date",
        "category",
        "quantity",
        "unit_price",
    }
    for row in _rows(path, fields):
        order_id = row["order_id"].strip()
        customer_id = row["customer_id"].strip()
        if not order_id or order_id in seen:
            raise ValueError("Order IDs must be present and unique")
        if customer_id not in known:
            raise ValueError(f"Unknown customer ID for order {order_id}")
        seen.add(order_id)
        try:
            quantity = int(row["quantity"])
            price = Decimal(row["unit_price"])
        except (ValueError, InvalidOperation) as error:
            raise ValueError(f"Invalid numeric value for order {order_id}") from error
        if quantity <= 0 or not price.is_finite() or price < 0:
            raise ValueError(f"Invalid quantity or price for order {order_id}")
        category = row["category"].strip()
        if not category:
            raise ValueError(f"Missing category for order {order_id}")
        result.append(
            Order(
                order_id,
                customer_id,
                date.fromisoformat(row["order_date"]),
                category,
                quantity,
                price,
            )
        )
    return result
