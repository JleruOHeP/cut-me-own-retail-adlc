# Cut-Me-Own Retail

A small Python analytics app for a fictional retailer. It reads synthetic customers and orders, then builds a **daily category sales report**. The open task in [TICKET.md](TICKET.md) is a new customer churn risk dataset; the starter project does not implement that feature.

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

## Data

- `data/customers.csv`: one row per fictional customer; contains synthetic email addresses that should be treated as PII for the exercise.
- `data/orders.csv`: individual line-item orders with a date, category, quantity, and unit price. Every order references a customer.
- The sample includes repeat buyers, lapsed buyers, recent joiners, and customers with no orders. It is fixed data so reruns are reproducible.

## Episode experiment

Start with a clean copy of this repo, open it in ChatGPT Codex, and ask it to read `AGENTS.md` and `TICKET.md`, inspect the repo, and present a plan **without editing files yet**. Review the plan and clarify the product rule when it asks. Then let Codex implement, test, and present evidence. The ticket is intentionally incomplete on churn thresholds because these require a product decision, not a developer guess.

