"""Public data types. All prices and quantities are integers (ticks / lots)."""

from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


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
    price: int  # resting (maker) price
    quantity: int


@dataclass(frozen=True)
class BookLevel:
    price: int
    quantity: int  # sum of remaining qty at this price (live orders only)
    order_count: int  # number of live orders at this price


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    bids: list[BookLevel]  # sorted price descending (best bid first)
    asks: list[BookLevel]  # sorted price ascending (best ask first)


@dataclass
class SubmitResult:
    order: Order  # post-match state
    trades: list[Trade]  # in match order; may be empty
