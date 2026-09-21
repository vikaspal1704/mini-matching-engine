# Mini Matching Engine

A minimal **limit-order matching engine** in Python — educational, in-memory, single-instrument.

Built as a portfolio project by **Vikas Pal** (Software Engineer, Fintech) to demonstrate real-time trading infrastructure fundamentals: price-time priority, order book mechanics, and a clean public API.

| | |
|---|---|
| **Status** | Docs-first — implementation pending |
| **Language** | Python 3.11+ |
| **License** | [MIT](LICENSE) |
| **Repo** | https://github.com/vikaspal1704/mini-matching-engine |

---

## What it is

- An in-memory **central limit order book (CLOB)** for a single symbol
- Price-time priority matching (FIFO within a price level)
- Public Python API: submit limit orders, cancel, query book / order state
- A small CLI demo that prints the book and generated trades
- Fully specified by docs so humans and AI coding agents can implement without guessing

## What it is not

- Not connected to any real exchange or market data feed
- Not a full trading system (no risk, no positions, no settlement)
- Not a web UI or persistent database
- Not multi-threaded / multi-instrument in v1

---

## Documentation (start here)

| Doc | Audience | Purpose |
|-----|----------|---------|
| [`docs/AGENT_BRIEF.md`](docs/AGENT_BRIEF.md) | **AI coding agents** | Primary build instructions — read this first |
| [`docs/PRD.md`](docs/PRD.md) | Recruiters / PMs | Goals, personas, functional requirements |
| [`docs/TRD.md`](docs/TRD.md) | Implementers | Language, layout, packaging, concurrency |
| [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) | Implementers | Exact types, method signatures, invariants |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Implementers / interviewers | Matching loop, price-time rules, worked example |
| [`docs/ACCEPTANCE_CRITERIA.md`](docs/ACCEPTANCE_CRITERIA.md) | QA / agents | Binary checklist for “done” |
| [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) | Implementers | Required pytest scenarios and edge cases |
| [`AGENTS.md`](AGENTS.md) | Agents | Short pointer to the brief |

---

## Stack (target)

- **Python** 3.11+
- **Packaging**: `pyproject.toml` (hatchling or setuptools)
- **Tests**: `pytest`
- **Lint** (optional): `ruff`
- **CI**: GitHub Actions (lint + test on push/PR)

---

## How to run (once implemented)

```bash
# Clone
git clone https://github.com/vikaspal1704/mini-matching-engine.git
cd mini-matching-engine

# Create venv and install (editable + test deps)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -q

# Run demo CLI
python -m demo.cli
```

Expected demo behavior: seed a few limit orders, print resulting trades and an order-book snapshot to stdout.

---

## Recruiter snapshot

| Topic | Detail |
|-------|--------|
| Domain | Limit order book / matching engine (fintech core) |
| Focus | Correctness, clear API contract, testability |
| Depth | Price-time priority, partial fills, cancel, book snapshot |
| Intent | Show systems thinking for remote hard-currency roles |

---

## License

MIT © 2026 Vikas Pal — see [LICENSE](LICENSE).
