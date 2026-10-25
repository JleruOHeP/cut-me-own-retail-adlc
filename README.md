# Cut-Me-Own Retail

A small Python analytics app for a fictional retailer. It reads synthetic customers and orders to build daily category sales and customer churn risk reports.

## Quick start

Python 3.11+ is required. From this directory:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e . -r requirements-dev.txt
python -m cmo_retail sales
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

The CLI writes `output/daily_sales.csv`. You may override `--customers`, `--orders`, and `--output`; see `python -m cmo_retail --help`. Output files are ignored by Git.

## Current report

`sales` groups orders by order date and category, then returns order count, units, gross revenue in synthetic dollars, and unique purchasing customers. Orders are linked to known customer IDs. Revenue uses decimal arithmetic. CSV output has a stable sort order and excludes customer emails.

## Customer churn report

```bash
python -m cmo_retail churn --as-of 2026-09-30
```

The required `--as-of YYYY-MM-DD` selects the report date explicitly; no current-date default is used. Output defaults to `output/customer_churn.csv`. Override `--customers`, `--orders`, or `--output` as for sales. Schedule this command daily with an explicit report date when needed.

The CSV contains one row per customer who joined on or before the report date, including customers with no purchases, sorted by `customer_id`, with these fields:

| Field | Meaning |
| --- | --- |
| `customer_id` | Source customer identifier |
| `days_since_last_purchase` | Calendar days since the latest purchase on or before the report date; blank if never purchased as of that date |
| `purchases_last_90_days` | Number of order records in the 90 calendar days ending on the report date (ages 0–89 days inclusive), not units |
| `spend_last_90_days` | Sum of quantity × unit price in that window, using decimal arithmetic and formatted to two decimal places |
| `churn_risk` | Priority under the rules below |

| Purchase history as of the report date | `churn_risk` |
| --- | --- |
| Last purchase 0–30 days ago | LOW |
| Last purchase 31–90 days ago | MEDIUM |
| Last purchase more than 90 days ago | HIGH |
| Never purchased; joined 0–30 days ago | MEDIUM |
| Never purchased; joined more than 30 days ago | HIGH |

Never-purchased customers have blank recency, zero purchases, and `0.00` spend. Their label is an **activation priority**: they have no purchasing habit to lose. The existing `churn_risk` column includes both uses for this exercise. These are illustrative rule-based segments, not model predictions.

Future purchases do not affect metrics or labels. A purchase exactly 90 days ago gives MEDIUM risk but falls outside the 90-day metrics window. Inputs must have unique customer and order IDs, known customer references, valid dates, positive quantities, and finite nonnegative prices. Customers joining after the report date are excluded, along with their orders, so later customer registrations do not block historical reports. Joining on the report date is included. Orders predating an included customer’s joining date are rejected. CSV parsing and ID/reference validation still apply to all source records; quantity, price, and chronology validation in the report applies to included customers, including their future orders. Invalid CLI input produces a generic error without raw source values. Derived rows exclude emails. Identical inputs and report date produce identical CSV bytes.

## Data

- `data/customers.csv`: one row per fictional customer; contains synthetic email addresses that should be treated as PII for the exercise.
- `data/orders.csv`: individual line-item orders with a date, category, quantity, and unit price. Every order references a customer.
- The sample includes repeat buyers, lapsed buyers, recent joiners, and customers with no orders. It is fixed data so reruns are reproducible.

## Episode experiment

Start with a clean copy of this repo, open it in ChatGPT Codex, and ask it to read `AGENTS.md` and `TICKET.md`, inspect the repo, and present a plan **without editing files yet**. Review the plan and clarify the product rule when it asks. Then let Codex implement, test, and present evidence. The ticket is intentionally incomplete on churn thresholds because these require a product decision, not a developer guess.

