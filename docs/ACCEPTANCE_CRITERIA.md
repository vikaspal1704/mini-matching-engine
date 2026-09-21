# Acceptance Criteria

Binary checklist. v1 is **done** only when every box is true.

---

## A. PRD MUST → verifiable criteria

| PRD ID | Criterion | How to verify |
|--------|-----------|---------------|
| F-MUST-1 | Limit BUY/SELL with positive int price & qty only | `test_reject_non_positive_price`, `test_reject_non_positive_quantity`, `test_submit_buy_and_sell_rest` |
| F-MUST-2 | Price-time priority | `test_time_priority_same_price`, `test_price_priority_across_levels` |
| F-MUST-3 | Trades at resting (maker) price | `test_trade_uses_resting_price` |
| F-MUST-4 | Partial fills rest residual | `test_partial_fill_rests_residual` |
| F-MUST-5 | Cancel open/partial; error on unknown/terminal | `test_cancel_open_order`, `test_cancel_unknown_raises`, `test_cancel_filled_raises` |
| F-MUST-6 | Public methods exist with contract signatures | Import + call smoke in tests; type shapes match API_CONTRACT |
| F-MUST-7 | Distinct order ids; no same-id collision | `test_order_ids_monotonic_unique` |
| F-MUST-8 | Invalid input → ValidationError, no silent clamp | `test_reject_non_positive_price`, `test_reject_non_positive_quantity` |
| F-MUST-9 | Symbol on constructor; echoed on orders/trades | `test_symbol_echoed_on_order_and_trade` |

---

## B. Required pytest scenarios (by exact test function name)

These function names MUST exist under `tests/` and pass:

| Test function | Intent |
|---------------|--------|
| `test_submit_buy_and_sell_rest` | Non-crossing orders rest on correct sides |
| `test_time_priority_same_price` | FIFO at one price (Example A) |
| `test_price_priority_across_levels` | Better price matches first (Example B) |
| `test_trade_uses_resting_price` | Aggressor buy @ 101 vs ask @ 100 → trade px 100 |
| `test_partial_fill_rests_residual` | Partial aggressor or resting residual |
| `test_cancel_open_order` | Cancel removes from book |
| `test_cancel_unknown_raises` | `OrderNotFoundError` |
| `test_cancel_filled_raises` | `OrderNotCancellableError` |
| `test_reject_non_positive_price` | `ValidationError` |
| `test_reject_non_positive_quantity` | `ValidationError` |
| `test_get_book_sorted_levels` | Bids desc, asks asc |
| `test_get_order_states` | OPEN → PARTIAL/FILLED transitions visible via get_order |
| `test_order_ids_monotonic_unique` | ids 1..n unique |
| `test_symbol_echoed_on_order_and_trade` | symbol match |
| `test_book_not_crossed_after_submit` | best_bid < best_ask when both sides live |
| `test_worked_example_canonical` | ARCHITECTURE §7 full sequence |

Additional tests from TEST_PLAN are encouraged; the table above is the **minimum name set**.

---

## C. Demo

- [ ] `python -m demo.cli` exits 0
- [ ] Stdout includes at least one trade line and a book representation
- [ ] Demo imports only public API (`matching_engine`)

---

## D. Packaging & CI

- [ ] `pyproject.toml` present; `pip install -e ".[dev]"` works
- [ ] `pytest -q` green locally
- [ ] `.github/workflows/ci.yml` runs pytest on push/PR
- [ ] CI green on default branch after merge

---

## E. Docs / README polish

- [ ] Root `README.md` replaced (no GitHub empty-repo placeholder text)
- [ ] README status updated when implementation lands (e.g. “Implemented — see tests/CI”)
- [ ] `LICENSE` is MIT © Vikas Pal 2026
- [ ] `AGENTS.md` points to `docs/AGENT_BRIEF.md`

---

## F. Definition of done (copy for agents)

```
DONE when:
1. All section A criteria pass via section B tests.
2. Section C demo runs.
3. Section D CI green.
4. Section E README is project README (not placeholder).
5. No public API divergence from API_CONTRACT.md.
```
