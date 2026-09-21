# Agent Brief — Mini Matching Engine

**Primary instructions for AI coding agents.**  
Author: Vikas Pal · Repo: https://github.com/vikaspal1704/mini-matching-engine

Read this file completely before writing code.

---

## 1. Mission

Implement an in-memory Python **limit-order matching engine** that matches [`API_CONTRACT.md`](API_CONTRACT.md) exactly, passes acceptance tests, ships a demo CLI, and keeps CI green.

**This repository may currently be docs-only.** You implement the code; do not change matching semantics that are already locked in the docs.

---

## 2. Read order (mandatory)

1. [`PRD.md`](PRD.md) — goals, MUST requirements, out of scope  
2. [`TRD.md`](TRD.md) — language, layout, packaging, errors, CI  
3. [`API_CONTRACT.md`](API_CONTRACT.md) — types, method signatures, invariants  
4. [`ARCHITECTURE.md`](ARCHITECTURE.md) — matching loop, maker price, worked example  
5. [`ACCEPTANCE_CRITERIA.md`](ACCEPTANCE_CRITERIA.md) — binary done checklist  
6. [`TEST_PLAN.md`](TEST_PLAN.md) — required test names and edge cases  

Then implement. If docs conflict, prefer **API_CONTRACT → ARCHITECTURE → PRD**.

---

## 3. Implementation phases

### Phase 1 — Core engine

- Create `pyproject.toml` and package `matching_engine/`
- Implement types, errors, `MatchingEngine` per API_CONTRACT
- Data structure: price → FIFO `deque` + order index (see TRD); improve only if documented in ARCHITECTURE
- Trade price = **resting (maker) price**
- Single-threaded, in-memory, integer price/qty

### Phase 2 — Tests

- Add all **required** pytest function names from ACCEPTANCE_CRITERIA / TEST_PLAN
- `test_worked_example_canonical` must follow ARCHITECTURE §7 exactly
- `pytest -q` green

### Phase 3 — Demo

- `demo/cli.py` with `python -m demo.cli`
- Seed a clear scenario (canonical example fine); print trades + book
- Public API only

### Phase 4 — CI / README polish

- `.github/workflows/ci.yml`: install `.[dev]`, run pytest (optional ruff)
- **Replace** any placeholder/default GitHub README content with the project README (recruiter overview + how to run + link to docs)
- Update README status from “docs-first / implementation pending” to implemented when code lands
- Ensure `LICENSE` (MIT, Vikas Pal 2026) and `AGENTS.md` remain correct

---

## 4. Do

- Follow signatures and error types literally  
- Use Python 3.11+  
- Keep matching deterministic  
- Map every F-MUST to a test  
- Prefer clarity over cleverness  
- After implementation on a branch: **open a PR** to `main` (do not only leave commits local)  
- When replacing README: keep links to `docs/*` and MIT license badge/mention  

## 5. Don’t

- Don’t invent market/stop/IOC/FOK orders  
- Don’t use `float` for price or quantity  
- Don’t add DB, network, auth, or UI  
- Don’t make v1 multi-threaded  
- Don’t silently clamp invalid inputs  
- Don’t price trades at the aggressor limit (maker/resting only)  
- Don’t leave the default GitHub “Description / Getting Started” placeholder README  
- Don’t skip `test_worked_example_canonical`  
- Don’t change public API without updating API_CONTRACT + tests in the same change  

---

## 6. Definition of done

Copy from ACCEPTANCE_CRITERIA:

```
DONE when:
1. All section A criteria pass via section B tests.
2. Section C demo runs.
3. Section D CI green.
4. Section E README is project README (not placeholder).
5. No public API divergence from API_CONTRACT.md.
```

---

## 7. Quick reference — public API

```python
from matching_engine import (
    MatchingEngine,
    OrderSide,
    OrderStatus,
    ValidationError,
    OrderNotFoundError,
    OrderNotCancellableError,
)

engine = MatchingEngine("DEMO")
result = engine.submit_limit(OrderSide.BUY, price=100, quantity=10)
engine.cancel(result.order.order_id)
book = engine.get_book()
order = engine.get_order(result.order.order_id)
```

Full types: [`API_CONTRACT.md`](API_CONTRACT.md).  
Worked example: [`ARCHITECTURE.md`](ARCHITECTURE.md) §7.

---

## 8. Git / PR expectations

- Branch name suggestion: `feat/core-matching-engine`  
- Commits: focused (engine → tests → demo → ci)  
- **Open a pull request** if working on a branch; PR description should cite acceptance checklist  
- Do not force-push `main`  

---

## 9. Out of scope reminder

No real exchange connectivity, no UI, no DB persistence, no auth.  
Educational correctness > micro-optimization.
