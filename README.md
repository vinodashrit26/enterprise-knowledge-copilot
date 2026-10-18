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
In development: Phase 0 (project setup) is nearly complete. The capabilities listed above are planned and are not implemented yet.

Completed so far (development setup only):

- Python 3.12 project managed with `uv`, using a `src/` layout and locked dependencies.
- Dev tools with strict settings: pytest (85% coverage minimum), Ruff, mypy, bandit and pip-audit.
- Pre-commit hooks for file hygiene, YAML/TOML checks, Ruff and secret scanning (gitleaks).
- A first unit test.
- A local PostgreSQL 17 database with the pgvector extension, run with Docker Compose.
- An environment template (`.env.example`).
- GitHub Actions CI and a pull request template.

## Quick start
Tested on macOS (Apple silicon). Other systems may need different install steps.

1. Install the tools with [Homebrew](https://brew.sh):
```bash
   brew install git uv docker docker-compose colima
```
   If `docker compose` is not recognized, add the following entry inside the top-level { } of `~/.docker/config.json`, with a comma after the entry before it if one exists:
```json
   "cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"]
```

2. Clone the repository:
```bash
   git clone https://github.com/vinodashrit26/enterprise-knowledge-copilot.git
   cd enterprise-knowledge-copilot
```

3. Create your local settings file. It is ignored by Git, so your values stay private:
```bash
   cp .env.example .env
```
   Edit `.env` and set `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and a matching `DATABASE_URL`. You can generate a password with `openssl rand -hex 16`. `ANTHROPIC_API_KEY` is not needed yet.

4. Install the Python dependencies (this also downloads Python 3.12):
```bash
   uv sync
```

5. Start the container engine and the database:
```bash
   colima start --cpu 2 --memory 4 --disk 30
   docker compose up -d
   docker compose ps
```
   The `db` container should show `healthy`. To confirm pgvector is enabled:
```bash
   docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT extname, extversion FROM pg_extension;"'
```

6. Install the pre-commit hooks (they run automatically on every commit):
```bash
   uv run pre-commit install
```

7. Run the checks:
```bash
   uv run pytest
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy
```

8. Stop everything when you are done:
```bash
   docker compose down
   colima stop
```
   Do not use `docker compose down -v` unless you want to delete the database data.

## Data and safety
All initial development and testing will use synthetic documents, fabricated customer scenarios, and mock APIs. No confidential employer information, production customer data, credentials, or proprietary source code will be included.

The planned system will enforce authorization and tenant isolation at the application and tool layers. State-changing operations will require explicit human approval. These controls will be validated through testing as the relevant capabilities are implemented.

## License
This project is released under the MIT License; see the `LICENSE` file.
