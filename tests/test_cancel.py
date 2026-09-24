import pytest

from matching_engine import (
    OrderNotCancellableError,
    OrderNotFoundError,
    OrderSide,
    OrderStatus,
)


def test_cancel_open_order(engine):
    order_id = engine.submit_limit(OrderSide.BUY, 100, 10).order.order_id

    cancelled = engine.cancel(order_id)

    assert cancelled.status is OrderStatus.CANCELLED
    assert engine.get_order(order_id).status is OrderStatus.CANCELLED
    snapshot = engine.get_book()
    assert snapshot.bids == [] and snapshot.asks == []


def test_cancel_partial_order(engine):
    engine.submit_limit(OrderSide.SELL, 100, 10)
    engine.submit_limit(OrderSide.BUY, 100, 4)

    cancelled = engine.cancel(1)

    assert cancelled.status is OrderStatus.CANCELLED
    assert engine.get_book().asks == []


def test_cancel_unknown_raises(engine):
    with pytest.raises(OrderNotFoundError):
        engine.cancel(999)


def test_cancel_filled_raises(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)
    engine.submit_limit(OrderSide.BUY, 100, 5)

    with pytest.raises(OrderNotCancellableError):
        engine.cancel(1)
    with pytest.raises(OrderNotCancellableError):
        engine.cancel(2)


def test_cancel_twice_raises(engine):
    engine.submit_limit(OrderSide.BUY, 100, 10)
    engine.cancel(1)

    with pytest.raises(OrderNotCancellableError):
        engine.cancel(1)


def test_cancelled_order_is_not_matched(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)
    engine.cancel(1)

    result = engine.submit_limit(OrderSide.BUY, 100, 5)

    assert result.trades == []
    assert result.order.status is OrderStatus.OPEN
