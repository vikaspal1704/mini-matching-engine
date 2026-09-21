# Product Requirements Document (PRD)

**Product:** Mini Matching Engine  
**Owner:** Vikas Pal  
**Version:** 1.0 (docs-first)  
**Status:** Spec locked for v1 implementation

---

## 1. Goals

1. Deliver a correct, educational, single-instrument **limit-order matching engine** in Python.
2. Expose a **stable public API** so callers (tests, CLI demo, future adapters) do not depend on internals.
3. Make the repo **recruiter-credible**: clear docs, runnable demo, green CI, MIT license.
4. Make the repo **agent-implementable**: unambiguous contracts, acceptance criteria, and test names — no guesswork on matching semantics.

## 2. Non-goals

- Real exchange connectivity (FIX, WebSocket market data, brokerage APIs)
- Graphical UI or web dashboard
- Database persistence or recovery after process restart
- Authentication, multi-tenancy, or user accounts
- Market orders, stop orders, iceberg, hidden liquidity (v1 = limit only)
- Multi-instrument or multi-threaded matching in v1
- Production latency SLAs or hardware optimization

## 3. Personas

| Persona | Needs |
|---------|--------|
| **Recruiter / hiring manager** | Understand what was built in ≤2 minutes from README; see seriousness (docs, tests, CI, license). |
| **Engineer interviewer** | Probe matching rules, complexity, edge cases; walk a worked example from docs. |
| **AI implementer** | Follow AGENT_BRIEF → contracts → acceptance; implement without inventing semantics. |

## 4. User stories / use cases

### Engine API

| ID | Story |
|----|--------|
| US-API-1 | As a caller, I submit a **limit buy** or **limit sell** and receive generated **trades** plus the resting order state (if any remaining quantity). |
| US-API-2 | As a caller, I **cancel** an open order by `order_id` and the book no longer shows that order. |
| US-API-3 | As a caller, I **query the book** and get bid/ask levels with aggregated size and (optionally) order counts. |
| US-API-4 | As a caller, I **get an order** by id and learn side, price, remaining qty, and status (`OPEN`, `PARTIAL`, `FILLED`, `CANCELLED`). |
| US-API-5 | As a caller, when my order crosses the book, I receive **zero or more trades** in price-time priority order until my order is filled or rests. |

### Demo CLI

| ID | Story |
|----|--------|
| US-CLI-1 | As a recruiter or interviewer, I run `python -m demo.cli` and see seeded orders, printed trades, and a final book snapshot without writing code. |
| US-CLI-2 | As an engineer, the demo uses only the public API (no private attributes). |

## 5. Functional requirements

### MUST

| ID | Requirement |
|----|-------------|
| F-MUST-1 | Support limit orders only: `BUY` / `SELL`, positive integer `quantity`, positive integer `price` (ticks as ints). |
| F-MUST-2 | Match using **price-time priority** (best price first; FIFO within a price level). |
| F-MUST-3 | Generate trades at the **resting (maker) price**. |
| F-MUST-4 | Support **partial fills**; residual quantity rests on the book at the limit price. |
| F-MUST-5 | Support **cancel** of an open / partially filled order; cancel of unknown / terminal order fails with a defined error. |
| F-MUST-6 | Expose `submit_limit`, `cancel`, `get_book`, `get_order` per `API_CONTRACT.md`. |
| F-MUST-7 | Self-trade prevention: an order must not match against another order with the same `order_id` (ids are unique; no same-id collision). Orders from different submissions always have distinct ids. |
| F-MUST-8 | Reject invalid input (qty ≤ 0, price ≤ 0, bad side) with a defined error type — do not silently clamp. |
| F-MUST-9 | Single symbol; symbol is a constructor parameter (string), stored and echoed on orders/trades. |

### SHOULD

| ID | Requirement |
|----|-------------|
| F-SHOULD-1 | Assign monotonically increasing integer `order_id` and `trade_id` starting at 1. |
| F-SHOULD-2 | Book snapshot includes best bid/ask levels sorted (bids descending, asks ascending). |
| F-SHOULD-3 | Demo CLI prints trades as they occur and a final book. |

### COULD

| ID | Requirement |
|----|-------------|
| F-COULD-1 | Optional `client_order_id` string on submit (stored, not used for matching). |
| F-COULD-2 | `get_depth(n)` helper limiting snapshot to top N levels. |
| F-COULD-3 | Structured logging of match/cancel events. |

## 6. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NF-1 | **Correctness over speed.** Prefer clear, testable code to micro-optimizations. |
| NF-2 | **Document O-complexity** of submit/cancel/get_book in ARCHITECTURE or TRD (big-O in terms of levels and orders at a level). Exact numbers not required for v1. |
| NF-3 | **Educational:** matching rules and one full worked example must be in docs. |
| NF-4 | **Single-threaded, in-memory** for v1 — no locks required if the process is single-threaded. |
| NF-5 | **Deterministic:** same sequence of submits/cancels → same trades and book state. |
| NF-6 | Python 3.11+, typed public surface (dataclasses or similar). |

## 7. Out of scope (explicit)

- No real exchange connectivity  
- No UI  
- No DB persistence required  
- No auth  
- No market / stop / IOC / FOK order types in v1 (limit GTC only: rest until filled or cancelled)

## 8. Worked example (summary)

Full step-by-step lives in [`ARCHITECTURE.md`](ARCHITECTURE.md) § Worked example. Summary:

1. Sell 10 @ 100 (id=1) rests.  
2. Sell 5 @ 100 (id=2) rests behind id=1 at same price.  
3. Buy 12 @ 100 (id=3) matches: Trade(1, buy=3, sell=1, qty=10, px=100), Trade(2, buy=3, sell=2, qty=2, px=100); order 2 remains 3 @ 100; order 3 filled.  

Final book: ask 100 × 3 (order 2 only). Bids empty.

## 9. Success metrics (v1)

- All MUST requirements mapped in `ACCEPTANCE_CRITERIA.md` and checked off  
- Named pytest scenarios from `TEST_PLAN.md` exist and pass  
- `python -m demo.cli` runs  
- CI green on GitHub Actions  
- README reflects implemented state (not empty placeholder)
