# Technical Requirements Document (TRD)

**Product:** Mini Matching Engine  
**Version:** 1.0

---

## 1. Language & runtime

- **Python 3.11+** (use `list[str]`, `X | Y` union syntax; no need for `from __future__ import annotations` unless preferred)
- CPython only for v1 (no PyPy requirement)

## 2. Packaging

| Item | Requirement |
|------|-------------|
| Manifest | `pyproject.toml` at repo root |
| Package name | `matching-engine` (distribution); import package `matching_engine` |
| Build backend | `hatchling` **or** `setuptools` (pick one; document in pyproject) |
| Install | `pip install -e ".[dev]"` |
| Dev extras | `pytest`, optionally `ruff`, `pytest-cov` |
| Python requires | `requires-python = ">=3.11"` |

### Suggested `pyproject.toml` shape (non-normative layout)

```toml
[project]
name = "matching-engine"
version = "0.1.0"
description = "Educational in-memory limit order matching engine"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "Vikas Pal" }]

[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.1"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["matching_engine"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 3. Repository layout

```
mini-matching-engine/
├── AGENTS.md
├── LICENSE
├── README.md
├── pyproject.toml
├── .github/
│   └── workflows/
│       └── ci.yml          # pytest (+ optional ruff)
├── matching_engine/        # OR engine/ — prefer matching_engine/
│   ├── __init__.py         # re-export public API
│   ├── types.py            # OrderSide, Order, Trade, BookLevel, ...
│   ├── errors.py           # MatchingEngineError hierarchy
│   ├── book.py             # OrderBook / price levels (internal OK)
│   └── engine.py           # MatchingEngine
├── demo/
│   ├── __init__.py
│   └── cli.py              # python -m demo.cli
├── tests/
│   ├── __init__.py
│   ├── test_submit_match.py
│   ├── test_cancel.py
│   ├── test_partial_fill.py
│   ├── test_price_time_priority.py
│   ├── test_validation.py
│   ├── test_get_book_order.py
│   └── test_worked_example.py
└── docs/
    └── *.md                # this documentation pack
```

Agents **must** use package name `matching_engine` unless they document a justified rename in ARCHITECTURE (not recommended).

## 4. Public API surface (contract summary)

Full types and invariants: [`API_CONTRACT.md`](API_CONTRACT.md).

```python
class MatchingEngine:
    def __init__(self, symbol: str) -> None: ...

    def submit_limit(
        self,
        side: OrderSide,
        price: int,
        quantity: int,
        *,
        client_order_id: str | None = None,
    ) -> SubmitResult: ...

    def cancel(self, order_id: int) -> Order: ...

    def get_book(self) -> OrderBookSnapshot: ...

    def get_order(self, order_id: int) -> Order: ...
```

Supporting types: `OrderSide`, `OrderStatus`, `Order`, `Trade`, `BookLevel`, `OrderBookSnapshot`, `SubmitResult`.

## 5. Data structures (recommendation)

| Structure | Role |
|-----------|------|
| **Bids map** | `dict[int, deque[Order]]` keyed by price; iterate keys descending for best bid |
| **Asks map** | `dict[int, deque[Order]]` keyed by price; iterate keys ascending for best ask |
| **Order index** | `dict[int, Order]` for O(1) `get_order` / cancel lookup |
| **Price level** | `collections.deque` of live orders — **FIFO** for time priority |

**Rationale:** Dict + deque is clear, correct for educational code, and O(1) append/popleft at a level. Finding best bid/ask is O(P) over distinct prices if scanning keys, or maintain sorted keys / `SortedDict` if desired.

**Agent may improve** (e.g. `sortedcontainers.SortedDict`, heap of prices) **if**:
1. Behavior and public API remain identical, and  
2. Change and complexity tradeoff are noted in `ARCHITECTURE.md`.

Do **not** use a flat unsorted list of all orders as the primary matching structure.

### Complexity targets (document in ARCHITECTURE)

| Operation | Expected (recommended structure) |
|-----------|----------------------------------|
| `submit_limit` (no match) | Amortized O(1) enqueue + index insert |
| `submit_limit` (match k trades) | O(k) plus best-price discovery cost |
| `cancel` | O(1) index lookup; O(L) to remove from deque of length L at that level (acceptable for v1); or mark cancelled and skip in match loop |
| `get_book` | O(P + N) to aggregate levels |
| `get_order` | O(1) |

Lazy cancel (tombstone + skip when matching) is acceptable if `get_book` / size aggregates exclude cancelled qty.

## 6. Error model

```text
MatchingEngineError(Exception)
├── ValidationError          # bad side/price/qty
├── OrderNotFoundError       # get_order / cancel unknown id
└── OrderNotCancellableError # already FILLED or CANCELLED
```

- Raise; do not return `None` for error paths on `cancel` / `get_order`.
- `submit_limit` validation → `ValidationError` before any book mutation.
- Messages should include the offending field/value when practical.

## 7. Concurrency

- **v1: single-threaded, in-memory.**
- No locks, no asyncio matching loop, no multiprocessing.
- Callers must not share one `MatchingEngine` instance across threads without external synchronization (document this one-liner in module docstring).

## 8. Logging / observability

- Minimal: optional `logging` debug/info on submit, trade, cancel.
- No metrics server, no OpenTelemetry requirement for v1.
- Demo CLI uses `print`, not a logging framework requirement.

## 9. CI (GitHub Actions)

Workflow `.github/workflows/ci.yml` MUST:

1. Trigger on `push` and `pull_request` to `main` (and optionally all branches).
2. Use Python 3.11 (matrix 3.11 / 3.12 is nice-to-have).
3. `pip install -e ".[dev]"` then `pytest -q`.
4. Optionally run `ruff check .` if ruff is in dev deps.

## 10. Demo module

- Entry: `python -m demo.cli`
- Uses only public API from `matching_engine`
- Seeds the worked example (or a clear variant) and prints trades + book
- Exit code 0 on success

## 11. Non-requirements (tech)

- No Redis, SQL, FastAPI, WebSockets in v1
- No binary protocols
- No numeric Decimal — **integer prices and quantities only**
