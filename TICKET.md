# JIRA-142 — Customer Churn Risk Dataset

## User story

As a retail analyst,
I want a daily customer churn-risk dataset
so that the marketing team can identify customers
who may stop purchasing.

## Acceptance criteria

- One record per customer.
- Output contains:
  - customer_id
  - days_since_last_purchase
  - purchases_last_90_days
  - spend_last_90_days
  - churn_risk
- churn_risk must be HIGH, MEDIUM or LOW.
- Transformation must be deterministic.
- Automated tests must be provided.
- Customer PII must not appear in logs.
- Documentation must describe the resulting dataset.
- Existing CI checks must pass.