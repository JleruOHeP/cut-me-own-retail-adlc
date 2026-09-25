# Cut-Me-Own Retail

## Project

This repository contains transformations used by the analytics team.

## Development

Install dependencies:

pip install -r requirements.txt

Run tests:

pytest

Run linting:

ruff check .

## Engineering principles

- Follow existing project conventions.
- Do not modify unrelated components.
- Add tests for new behaviour.
- Do not expose customer PII in logs.
- Keep transformations deterministic.
- Update documentation when interfaces change.

## Workflow

Before implementing a ticket:

1. Inspect the relevant parts of the repository.
2. Produce an implementation plan.
3. Identify assumptions or ambiguities.
4. Wait for approval before modifying files.

After implementation:

1. Run tests and static checks.
2. Review your changes.
3. Map evidence to the ticket acceptance criteria.
4. Summarise remaining risks or uncertainties.