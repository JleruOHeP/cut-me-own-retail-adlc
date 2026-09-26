# Cut-Me-Own Retail

A small Python analytics app for a fictional retailer. It reads synthetic customers and orders, then builds daily category sales and customer churn risk reports.

## Quick start

Python 3.11+ is required. From this directory:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e . -r requirements-dev.txt
python -m cmo_retail sales
python -m cmo_retail churn --as-of 2026-09-30
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

The sales command writes `output/daily_sales.csv`; the churn command writes `output/customer_churn_risk.csv`. You may override `--customers`, `--orders`, and `--output`; see `python -m cmo_retail --help`. Output files are ignored by Git.

## Current report

`sales` groups orders by order date and category, then returns order count, units, gross revenue in synthetic dollars, and unique purchasing customers. Orders are linked to known customer IDs. Revenue uses decimal arithmetic. CSV output has a stable sort order and excludes customer emails.

## Customer churn risk report

Run `python -m cmo_retail churn --as-of YYYY-MM-DD`. The report has one row per customer who joined on or before that date, sorted by customer ID, with `customer_id`, `days_since_last_purchase`, `purchases_last_90_days`, `spend_last_90_days`, and `churn_risk`. Customers who join later are excluded. The required as-of date makes runs reproducible. Only purchases on or before that date count. The 90-day window includes the as-of date and the preceding 89 days. Spend is quantity times unit price, shown in synthetic dollars with two decimal places. Each order row counts as one purchase.

For customers who have purchased, `churn_risk` is `LOW` when the last purchase was 0–30 days ago, `MEDIUM` at 31–90 days, and `HIGH` after 90 days. For customers who have never purchased as of the report date, the last-purchase field is blank and both 90-day measures are zero. Their label is `MEDIUM` when they joined 0–30 days ago and `HIGH` after 30 days. For these customers, the label is an **activation priority**, since there is no purchasing habit to lose. This is an illustrative rule-based segment, not a trained prediction model.

The report rejects orders dated before their customer's join date. Source email addresses are never included in the derived report or normal command output.

## Data

- `data/customers.csv`: one row per fictional customer; contains synthetic email addresses that should be treated as PII for the exercise.
- `data/orders.csv`: individual line-item orders with a date, category, quantity, and unit price. Every order references a customer.
- The sample includes repeat buyers, lapsed buyers, recent joiners, and customers with no orders. It is fixed data so reruns are reproducible.

## Episode experiment

Start with a clean copy of this repo, open it in ChatGPT Codex, and ask it to read `AGENTS.md` and `TICKET.md`, inspect the repo, and present a plan **without editing files yet**. Review the plan and clarify the product rule when it asks. Then let Codex implement, test, and present evidence. The ticket is intentionally incomplete on churn thresholds because these require a product decision, not a developer guess.

