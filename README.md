# Enterprise Knowledge & Workflow Copilot
An AI-powered platform designed to help enterprise operations teams investigate customer onboarding issues, find evidence across technical documentation, identify potential root causes, and plan safe, auditable remediation workflows.

[![CI](https://github.com/vinodashrit26/enterprise-knowledge-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/vinodashrit26/enterprise-knowledge-copilot/actions/workflows/ci.yml)

## The problem
Enterprise onboarding and troubleshooting often require teams to search multiple documents, review configuration details, inspect logs, and manually correlate information across systems. This process can be time-consuming, difficult to reproduce, and prone to missed information.

The Enterprise Knowledge & Workflow Copilot aims to reduce the time and risk involved in this process by combining enterprise knowledge retrieval with structured investigation and controlled workflow automation.

## Planned capabilities
The project will be developed incrementally, with the following planned capabilities:

- **Enterprise Knowledge Assistant:** Answer questions using relevant documentation and provide evidence-backed responses with citations.
- **Investigation Engine:** Combine document retrieval and structured system data to investigate onboarding issues and identify potential root causes.
- **Multi-Agent Workflow:** Coordinate specialized agents for research, diagnosis, policy validation, and remediation planning.
- **Controlled Workflow Execution:** Integrate with mock APIs to validate configurations and execute approved actions, with human approval for state-changing operations.
- **Quality and Governance:** Evaluate response quality, retrieval accuracy, and task completion while incorporating server-side authorization, tenant isolation, observability, and audit trails.

## Status
In development: Phase 0 setup is almost complete

Following capabilities are implemented
- Initialized the Python project with `uv` (Python 3.12, `src/` layout, locked dependencies in `uv.lock`).
- Added dev tools (pytest, pytest-cov, Ruff, mypy, bandit, pip-audit, pre-commit) and their settings in `pyproject.toml`: strict mypy, Ruff with Google-style docstrings, 85% coverage minimum.
- Added the first unit test (`tests/unit/test_main.py`).
- Added pre-commit hooks (`.pre-commit-config.yaml`): file hygiene, YAML/TOML checks, Ruff, and gitleaks secret scanning.
- Added a local PostgreSQL 17 database with the pgvector extension (`docker-compose.yml` and an init script that enables the extension).
- Added `.env.example` to document the required environment variables (fake values only).
- Added the GitHub Actions CI workflow (`.github/workflows/ci.yml`) and this pull request template.
- Updated `.gitignore` (macOS `.DS_Store`, local notes).

## Data and safety
All initial development and testing will use synthetic documents, fabricated customer scenarios, and mock APIs. No confidential employer information, production customer data, credentials, or proprietary source code will be included.

The planned system will enforce authorization and tenant isolation at the application and tool layers. State-changing operations will require explicit human approval. These controls will be validated through testing as the relevant capabilities are implemented.

## License
This project is released under the MIT License, see the LICENSE file.

## Quick start
Install the tools that are not in the repo: Git, Homebrew, Colima, docker, docker-compose, uv. Set up a new SSH key and add it to GitHub.
git clone the repo.
cp .env.example .env, then fill in your own values (database password, API key).
uv sync (uses pyproject.toml, uv.lock, .python-version).
colima start, then docker compose up -d (uses docker-compose.yml and the init script).
uv run pre-commit install.
Not in the repo, so copy it yourself: revision.md and .env. (The README has no setup guide yet. That is a gap.)
