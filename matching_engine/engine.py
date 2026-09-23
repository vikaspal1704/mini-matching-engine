"""Price-time priority limit order matching engine for a single symbol.

Single-threaded and in-memory: do not share one ``MatchingEngine`` instance across
threads without external synchronization.
"""

import logging
from dataclasses import replace

from .book import OrderBook
from .errors import OrderNotCancellableError, OrderNotFoundError, ValidationError
from .types import Order, OrderBookSnapshot, OrderSide, OrderStatus, SubmitResult, Trade

logger = logging.getLogger(__name__)

_TERMINAL = (OrderStatus.FILLED, OrderStatus.CANCELLED)


def _is_int(value: object) -> bool:
    # bool is a subclass of int but is never a meaningful price or quantity.
    return isinstance(value, int) and not isinstance(value, bool)


def _crosses(aggressor: Order, resting_price: int) -> bool:
    if aggressor.side is OrderSide.BUY:
        return resting_price <= aggressor.price
    return resting_price >= aggressor.price


def _update_status(order: Order) -> None:
    if order.remaining_quantity == 0:
        order.status = OrderStatus.FILLED
    elif order.remaining_quantity < order.original_quantity:
        order.status = OrderStatus.PARTIAL


class MatchingEngine:
    def __init__(self, symbol: str) -> None:
        """Create an empty book for ``symbol``.

        Raises ValidationError if symbol is empty or not a str.
        """
        if not isinstance(symbol, str) or not symbol:
            raise ValidationError(f"symbol must be a non-empty str, got {symbol!r}")
        self._symbol = symbol
        self._book = OrderBook()
        self._orders: dict[int, Order] = {}
        self._next_order_id = 1
        self._next_trade_id = 1

    @property
    def symbol(self) -> str:
        return self._symbol

    def submit_limit(
        self,
        side: OrderSide,
        price: int,
        quantity: int,
        *,
        client_order_id: str | None = None,
    ) -> SubmitResult:
        """Validate, assign order_id, match, rest residual if any.

        Returns SubmitResult with final order state and trades (possibly empty).
        Raises ValidationError on invalid side/price/quantity.
        """
        self._validate(side, price, quantity, client_order_id)

        order = Order(
            order_id=self._next_order_id,
            symbol=self._symbol,
            side=side,
            price=price,
            original_quantity=quantity,
            remaining_quantity=quantity,
            status=OrderStatus.OPEN,
            client_order_id=client_order_id,
        )
        self._next_order_id += 1
        self._orders[order.order_id] = order

        trades = self._match(order)
        if order.remaining_quantity > 0:
            self._book.side(order.side).append(order)
        logger.debug("submitted order %s with %d trade(s)", order.order_id, len(trades))
        return SubmitResult(order=replace(order), trades=trades)

    def cancel(self, order_id: int) -> Order:
        """Cancel an OPEN or PARTIAL order.

        Returns the order with status CANCELLED.
        Raises OrderNotFoundError if id unknown.
        Raises OrderNotCancellableError if FILLED or CANCELLED.
        """
        order = self._lookup(order_id)
        if order.status in _TERMINAL:
            raise OrderNotCancellableError(
                f"order {order_id} is {order.status.value} and cannot be cancelled"
            )
        self._book.side(order.side).remove(order)
        order.status = OrderStatus.CANCELLED
        logger.debug("cancelled order %s", order_id)
        return replace(order)

    def get_book(self) -> OrderBookSnapshot:
        """Return current aggregated book. Never raises for empty book."""
        return OrderBookSnapshot(
            symbol=self._symbol,
            bids=self._book.bids.levels(),
            asks=self._book.asks.levels(),
        )

    def get_order(self, order_id: int) -> Order:
        """Return current order state, including FILLED / CANCELLED orders.

        Raises OrderNotFoundError if id never existed.
        """
        return replace(self._lookup(order_id))

    def _lookup(self, order_id: int) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"unknown order_id {order_id!r}")
        return order

    @staticmethod
    def _validate(side: object, price: object, quantity: object, client_order_id: object) -> None:
        if not isinstance(side, OrderSide):
            raise ValidationError(f"side must be an OrderSide, got {side!r}")
        if not _is_int(price):
            raise ValidationError(f"price must be an int, got {price!r}")
        if price <= 0:
            raise ValidationError(f"price must be >= 1, got {price}")
        if not _is_int(quantity):
            raise ValidationError(f"quantity must be an int, got {quantity!r}")
        if quantity <= 0:
            raise ValidationError(f"quantity must be >= 1, got {quantity}")
        if client_order_id is not None and not isinstance(client_order_id, str):
            raise ValidationError(f"client_order_id must be a str or None, got {client_order_id!r}")

    def _match(self, order: Order) -> list[Trade]:
        opposite = self._book.opposite(order.side)
        trades: list[Trade] = []

        while order.remaining_quantity > 0:
            best = opposite.best_price()
            if best is None or not _crosses(order, best):
                break
            resting = opposite.head(best)
            fill_qty = min(order.remaining_quantity, resting.remaining_quantity)
            buy, sell = (order, resting) if order.side is OrderSide.BUY else (resting, order)
            trades.append(
                Trade(
                    trade_id=self._next_trade_id,
                    symbol=self._symbol,
                    buy_order_id=buy.order_id,
                    sell_order_id=sell.order_id,
                    price=resting.price,  # maker / resting price
                    quantity=fill_qty,
                )
            )
            self._next_trade_id += 1
            order.remaining_quantity -= fill_qty
            resting.remaining_quantity -= fill_qty
            _update_status(order)
            _update_status(resting)
            if resting.remaining_quantity == 0:
                opposite.pop_head(best)

        return trades
