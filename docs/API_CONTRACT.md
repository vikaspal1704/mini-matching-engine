# API Contract

**Normative.** Implementations MUST match these types and behaviors.  
Import path: `from matching_engine import ...` (re-exported from package root).

---

## 1. Enumerations

```python
from enum import Enum

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
```

---

## 2. Data types

All monetary/size fields are **`int`** (ticks / lots). No `float`. No `Decimal` required.

```python
from dataclasses import dataclass

@dataclass
class Order:
    order_id: int
    symbol: str
    side: OrderSide
    price: int
    original_quantity: int
    remaining_quantity: int
    status: OrderStatus
    client_order_id: str | None = None

@dataclass(frozen=True)
class Trade:
    trade_id: int
    symbol: str
    buy_order_id: int
    sell_order_id: int
    price: int          # resting (maker) price
    quantity: int

@dataclass(frozen=True)
class BookLevel:
    price: int
    quantity: int       # sum of remaining qty at this price (live orders only)
    order_count: int    # number of live orders at this price

@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    bids: list[BookLevel]   # sorted price descending (best bid first)
    asks: list[BookLevel]   # sorted price ascending (best ask first)

@dataclass
class SubmitResult:
    order: Order            # post-match state
    trades: list[Trade]     # in match order; may be empty
```

### Field rules

| Field | Rule |
|-------|------|
| `order_id` / `trade_id` | Positive ints; engine-assigned; start at **1**; monotonically increasing per engine instance |
| `price` | Must be `>= 1` on submit |
| `original_quantity` | Set at creation; never decreases |
| `remaining_quantity` | `0 <= remaining <= original`; `0` iff `FILLED` |
| `bids` / `asks` | Omit empty levels; do not include cancelled/filled orders’ qty |

---

## 3. MatchingEngine

```python
class MatchingEngine:
    def __init__(self, symbol: str) -> None:
        """
        Create an empty book for `symbol`.
        Raises ValidationError if symbol is empty or not a str.
        """

    def submit_limit(
        self,
        side: OrderSide,
        price: int,
        quantity: int,
        *,
        client_order_id: str | None = None,
    ) -> SubmitResult:
        """
        Validate, assign order_id, match, rest residual if any.
        Returns SubmitResult with final order state and trades (possibly empty).
        Raises ValidationError on invalid side/price/quantity.
        """

    def cancel(self, order_id: int) -> Order:
        """
        Cancel an OPEN or PARTIAL order.
        Returns the order with status CANCELLED.
        Raises OrderNotFoundError if id unknown.
        Raises OrderNotCancellableError if FILLED or CANCELLED.
        """

    def get_book(self) -> OrderBookSnapshot:
        """Return current aggregated book. Never raises for empty book."""

    def get_order(self, order_id: int) -> Order:
        """
        Return current order state (including FILLED / CANCELLED if still indexed).
        Raises OrderNotFoundError if id never existed.
        Filled/cancelled orders SHOULD remain retrievable for the life of the process.
        """
```

### Constructor notes

- `symbol` is stored and copied onto every `Order` and `Trade` created by this instance.
- One engine instance = one symbol. Do not accept per-order symbol overrides in v1.

---

## 4. Errors

```python
class MatchingEngineError(Exception):
    """Base for all engine errors."""

class ValidationError(MatchingEngineError):
    """Invalid arguments (price, qty, side, symbol)."""

class OrderNotFoundError(MatchingEngineError):
    """Unknown order_id."""

class OrderNotCancellableError(MatchingEngineError):
    """Order exists but is FILLED or already CANCELLED."""
```

### Validation matrix for `submit_limit`

| Condition | Error |
|-----------|--------|
| `side` not `OrderSide.BUY` / `SELL` | `ValidationError` |
| `price <= 0` | `ValidationError` |
| `quantity <= 0` | `ValidationError` |
| non-int price/qty (if type-check performed) | `ValidationError` or `TypeError` (prefer ValidationError if wrapping) |

No book mutation before successful validation.

---

## 5. Behavioral invariants

These are **testable** and MUST hold after every successful public call:

1. **Conservation:** For any order, `filled = original_quantity - remaining_quantity`; sum of that order’s trade quantities equals `filled`.
2. **Trade price:** Every trade’s `price` equals the resting order’s limit price at fill time.
3. **Sides:** `buy_order_id` refers to a BUY order; `sell_order_id` to a SELL order.
4. **Book consistency:** Sum of `BookLevel.quantity` on bids (asks) equals sum of `remaining_quantity` of all OPEN/PARTIAL BUY (SELL) orders.
5. **Best prices:** If both sides non-empty, best bid price ≤ best ask price **or** the book is crossed only transiently inside matching — after `submit_limit` returns, book MUST NOT be crossed (best_bid < best_ask, or one side empty). Wait: actually after matching completes, resting book should never be crossed: `best_bid < best_ask` when both exist. Strict: `best_bid < best_ask` (equal prices would have matched). When both sides have orders, `max(bid prices) < min(ask prices)`.
6. **FIFO:** At a single price level, earlier `order_id` (lower id if ids are monotonic with time) is ahead in the queue; first to match.
7. **Id uniqueness:** No two orders share `order_id`; no two trades share `trade_id` within one engine.
8. **Cancel:** After successful cancel, order not in book aggregates; `get_order` returns `CANCELLED`.
9. **Determinism:** Identical call sequences on fresh engines → identical ids, trades, and snapshots.

---

## 6. Non-guarantees

- Stability of object identity for `Order` across calls (may return copies; field values must be correct).
- Persistence across process restart.
- Thread safety.

---

## 7. Package `__init__` exports

```python
__all__ = [
    "OrderSide",
    "OrderStatus",
    "Order",
    "Trade",
    "BookLevel",
    "OrderBookSnapshot",
    "SubmitResult",
    "MatchingEngine",
    "MatchingEngineError",
    "ValidationError",
    "OrderNotFoundError",
    "OrderNotCancellableError",
]
```
