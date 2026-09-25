"""Input records shared by the reporting pipeline."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Customer:
    customer_id: str
    email: str
    joined_at: date


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    order_date: date
    category: str
    quantity: int
    unit_price: Decimal
