# Test Plan

**Framework:** pytest  
**Location:** `tests/`  
**Rule:** Prefer Arrange-Act-Assert; one behavior per test; use exact function names required by ACCEPTANCE_CRITERIA.

---

## 1. Matrix overview

| Area | Must cover |
|------|------------|
| Validation | price ≤ 0, qty ≤ 0, empty symbol |
| Resting | buy-only, sell-only, both sides non-crossing |
| Matching | full fill, partial fill, multi-level sweep |
| Priority | time (FIFO), price (best first) |
| Trade price | always maker/resting |
| Cancel | open, partial, unknown, filled, double-cancel |
| Queries | get_book sorting/aggregation, get_order statuses |
| Invariants | uncrossed book, conservation of qty, unique ids |
| Canonical | ARCHITECTURE worked example |

---

## 2. Required tests (names + scenario)

### Validation

| Test | Setup | Expect |
|------|-------|--------|
| `test_reject_non_positive_price` | `submit_limit(BUY, 0, 1)` and/or `price=-1` | `ValidationError`; book empty |
| `test_reject_non_positive_quantity` | `quantity=0` or `-5` | `ValidationError` |
| `test_reject_empty_symbol` | `MatchingEngine("")` | `ValidationError` |

### Resting / book shape

| Test | Setup | Expect |
|------|-------|--------|
| `test_submit_buy_and_sell_rest` | BUY 10@100; SELL 5@101 | No trades; bids `[100×10]`; asks `[101×5]` |
| `test_get_book_sorted_levels` | Bids 100, 99; Asks 101, 102 | bids prices `[100,99]`; asks `[101,102]` |
| `test_book_aggregates_same_price` | Two BUY @100 qty 3 and 7 | One bid level `100`, qty `10`, order_count `2` |

### Priority & matching

| Test | Setup | Expect |
|------|-------|--------|
| `test_time_priority_same_price` | SELL 10@100 (id1), SELL 5@100 (id2), BUY 12@100 | Trades: 10 vs id1 @100, then 2 vs id2 @100; id2 rem 3 |
| `test_price_priority_across_levels` | SELL 4@99, SELL 4@100, BUY 6@100 | First trade px=99 qty=4; second px=100 qty=2 |
| `test_trade_uses_resting_price` | SELL 5@100; BUY 5@105 | Single trade price **100** (not 105) |
| `test_partial_fill_rests_residual` | SELL 10@50; BUY 4@50 | Trade qty 4; sell remaining 6 OPEN/PARTIAL; buy FILLED |
| `test_aggressor_partial_rests` | SELL 3@50; BUY 10@50 | Trade qty 3; buy rests 7@50 |
| `test_multi_trade_single_submit` | Multiple resting sells; large buy | `len(trades) >= 2`; aggressor filled or rested correctly |
| `test_no_match_when_buy_below_ask` | Ask 100; Buy 99 | trades=[]; both rest |

### Cancel

| Test | Setup | Expect |
|------|-------|--------|
| `test_cancel_open_order` | Rest buy; cancel | status CANCELLED; book empty |
| `test_cancel_partial_order` | Partially fill sell; cancel residual | CANCELLED; book empty of that order |
| `test_cancel_unknown_raises` | `cancel(999)` on fresh engine | `OrderNotFoundError` |
| `test_cancel_filled_raises` | Fully fill; `cancel` | `OrderNotCancellableError` |
| `test_cancel_twice_raises` | Cancel once then again | second → `OrderNotCancellableError` |

### Queries / ids / symbol

| Test | Setup | Expect |
|------|-------|--------|
| `test_get_order_states` | Submit resting; then hit partial; get_order each time | OPEN then PARTIAL (or FILLED) |
| `test_order_ids_monotonic_unique` | 5 submits | ids `{1,2,3,4,5}` |
| `test_trade_ids_monotonic` | Produce 3 trades | trade_ids 1..3 |
| `test_symbol_echoed_on_order_and_trade` | `MatchingEngine("ABC")` + match | order.symbol and trade.symbol == `"ABC"` |
| `test_book_not_crossed_after_submit` | Random-ish sequence of crossing/non-crossing | after each submit, if both sides non-empty: `bids[0].price < asks[0].price` |
| `test_get_order_not_found` | `get_order(1)` on empty | `OrderNotFoundError` |

### Canonical

| Test | Setup | Expect |
|------|-------|--------|
| `test_worked_example_canonical` | Exact ARCHITECTURE §7 steps 1–5 | Exact trade list and final empty book after cancel |

---

## 3. Edge cases (should include)

| Case | Notes |
|------|-------|
| Exact qty match clears level | order_count → 0; level omitted from snapshot |
| Sweep entire ask side | asks empty; residual buy rests |
| Cancel head of FIFO then match | next order at level becomes first |
| Cancel middle of FIFO | remaining orders keep relative order |
| Large qty sweep many levels | conservation: sum trade qtys == aggressor filled |
| `client_order_id` round-trip | if implemented (COULD); store on Order |

---

## 4. Non-goals for tests

- Load / performance benchmarks not required for v1 acceptance
- Concurrency / race tests not required (single-threaded)
- Property-based fuzzing optional (Hypothesis nice-to-have)

---

## 5. Commands

```bash
pip install -e ".[dev]"
pytest -q
pytest -q tests/test_worked_example.py  # optional path split
```

CI MUST run the full suite with no skips for required tests.
