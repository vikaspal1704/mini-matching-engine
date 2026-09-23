"""Internal order book: price levels of FIFO queues for each side.

Not part of the public API. Bids and asks are ``dict[int, deque[Order]]`` keyed by
price; best price is found by scanning keys (O(P) in distinct price levels).
"""

from collections import deque

from .types import BookLevel, Order, OrderSide


class _SideBook:
    """One side of the book. ``descending`` is True for bids (higher is better)."""

    def __init__(self, descending: bool) -> None:
        self._descending = descending
        self._levels: dict[int, deque[Order]] = {}

    def best_price(self) -> int | None:
        if not self._levels:
            return None
        return max(self._levels) if self._descending else min(self._levels)

    def head(self, price: int) -> Order:
        return self._levels[price][0]

    def pop_head(self, price: int) -> None:
        queue = self._levels[price]
        queue.popleft()
        if not queue:
            del self._levels[price]

    def append(self, order: Order) -> None:
        self._levels.setdefault(order.price, deque()).append(order)

    def remove(self, order: Order) -> None:
        queue = self._levels[order.price]
        queue.remove(order)
        if not queue:
            del self._levels[order.price]

    def levels(self) -> list[BookLevel]:
        prices = sorted(self._levels, reverse=self._descending)
        return [
            BookLevel(
                price=price,
                quantity=sum(o.remaining_quantity for o in self._levels[price]),
                order_count=len(self._levels[price]),
            )
            for price in prices
        ]


class OrderBook:
    """Bids and asks for a single symbol."""

    def __init__(self) -> None:
        self.bids = _SideBook(descending=True)
        self.asks = _SideBook(descending=False)

    def side(self, side: OrderSide) -> _SideBook:
        return self.bids if side is OrderSide.BUY else self.asks

    def opposite(self, side: OrderSide) -> _SideBook:
        return self.asks if side is OrderSide.BUY else self.bids
