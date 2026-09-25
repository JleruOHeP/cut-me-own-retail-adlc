"""Regenerate the fixed, fictional input CSVs for the episode."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rng = random.Random(142)
    with (DATA / "customers.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["customer_id", "email", "joined_at"])
        for number in range(1, 19):
            joined = date(2025, 1, 1) + timedelta(days=(number * 29) % 450)
            writer.writerow(
                [f"C{number:03d}", f"customer{number:03d}@example.test", joined]
            )

    # Buyer groups cover recent, intermittent, older, and zero-order histories.
    orders = []
    categories = ["Books", "Garden", "Home", "Outdoor"]
    for number in range(1, 17):
        joined = date(2025, 1, 1) + timedelta(days=(number * 29) % 450)
        if number <= 5:
            offsets = [10, 42, 76, 126]
        elif number <= 10:
            offsets = [55, 100, 174]
        elif number <= 14:
            offsets = [130, 210]
        else:
            offsets = [250]
        for position, offset in enumerate(offsets):
            day = date(2026, 9, 25) - timedelta(days=offset + rng.randrange(-6, 7))
            if day < joined:
                continue
            orders.append(
                [
                    "",
                    f"C{number:03d}",
                    day.isoformat(),
                    categories[(number + position) % len(categories)],
                    rng.randint(1, 4),
                    f"{rng.choice([12, 24, 39, 58])}.50",
                ]
            )

    orders.sort(key=lambda row: (row[2], row[1]))
    with (DATA / "orders.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "order_id",
                "customer_id",
                "order_date",
                "category",
                "quantity",
                "unit_price",
            ]
        )
        for number, order in enumerate(orders, 1):
            order[0] = f"O{number:04d}"
            writer.writerow(order)


if __name__ == "__main__":
    main()
