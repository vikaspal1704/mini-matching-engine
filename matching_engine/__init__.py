"""Educational in-memory limit order matching engine (single symbol, price-time priority)."""

from .engine import MatchingEngine
from .errors import (
    MatchingEngineError,
    OrderNotCancellableError,
    OrderNotFoundError,
    ValidationError,
)
from .types import BookLevel, Order, OrderBookSnapshot, OrderSide, OrderStatus, SubmitResult, Trade

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
