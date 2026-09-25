# JIRA-142 — Daily customer churn risk dataset

## User story

As a retail analyst, I want a daily customer churn risk dataset so the marketing team can identify customers who may stop purchasing.

## Acceptance criteria

- Produce one row per customer, including customers with no orders.
- The output has `customer_id`, `days_since_last_purchase`, `purchases_last_90_days`, `spend_last_90_days`, and `churn_risk`.
- `churn_risk` is `HIGH`, `MEDIUM`, or `LOW`.
- A caller can choose an **as-of date**. Running with the same inputs and date produces identical output.
- Add meaningful automated tests for boundary cases and data quality.
- Do not expose customer email addresses or other customer PII in logs or in the derived dataset.
- Document how to run the report and interpret its output.
- Existing checks and the new feature pass CI.

## Product context

The marketing team will use this as a prioritization aid. The input is synthetic. This is an illustrative rule-based segment, not a trained prediction model.

## Open product decision

Marketing has not defined what counts as `HIGH`, `MEDIUM`, or `LOW`, or how to classify a customer who has never purchased. Confirm the business rule with the product owner before choosing thresholds.
