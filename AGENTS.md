# Cut-Me-Own Retail: working agreement

This repository contains a small analytics reporting application for fictional retail data.

## Development

- Install in a virtual environment: `python -m pip install -e . -r requirements-dev.txt`
- Run tests: `python -m unittest discover -s tests -v`
- Run lint: `ruff check .`
- Check formatting: `ruff format --check .`
- Run the existing report: `python -m cmo_retail sales`

## Engineering principles

- Follow established patterns and keep changes within the ticket's scope.
- Add meaningful tests for new behavior and update user-facing documentation.
- Keep transformations deterministic; avoid dependencies on the current date.
- Source data contains customer emails. Do not expose emails or other customer PII in logs or derived reports.
- No network services, external credentials, or production systems are required.

## Ticket workflow

1. Inspect the ticket, repository, tests, documentation, and CI configuration.
2. Present a plan and identify assumptions, ambiguities, and risks.
3. Wait for the human to approve the plan before changing files.
4. Implement and run local checks; inspect the diff.
5. Map each acceptance criterion to observable evidence. State what remains unverified.
