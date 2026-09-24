"""ARCHITECTURE.md §7 — full worked example (canonical)."""

from matching_engine import (
    BookLevel,
    MatchingEngine,
    OrderSide,
    OrderStatus,
    Trade,
)


def test_worked_example_canonical():
    engine = MatchingEngine("DEMO")

    # Step 1
    step1 = engine.submit_limit(OrderSide.SELL, 100, 10)
    assert step1.order.order_id == 1
    assert step1.order.status is OrderStatus.OPEN
    assert step1.trades == []

    # Step 2
    step2 = engine.submit_limit(OrderSide.SELL, 100, 5)
    assert step2.order.order_id == 2
    assert step2.order.status is OrderStatus.OPEN
    assert step2.trades == []

    # Step 3
    step3 = engine.submit_limit(OrderSide.BUY, 101, 3)
    assert step3.order.order_id == 3
    assert step3.order.status is OrderStatus.FILLED
    assert step3.trades == [
        Trade(trade_id=1, symbol="DEMO", buy_order_id=3, sell_order_id=1, price=100, quantity=3)
    ]
    assert engine.get_order(1).remaining_quantity == 7

    # Step 4
    step4 = engine.submit_limit(OrderSide.BUY, 100, 10)
    assert step4.order.order_id == 4
    assert step4.order.status is OrderStatus.FILLED
    assert step4.trades == [
        Trade(trade_id=2, symbol="DEMO", buy_order_id=4, sell_order_id=1, price=100, quantity=7),
        Trade(trade_id=3, symbol="DEMO", buy_order_id=4, sell_order_id=2, price=100, quantity=3),
    ]
    assert engine.get_order(1).status is OrderStatus.FILLED
    order_2 = engine.get_order(2)
    assert order_2.status is OrderStatus.PARTIAL
    assert order_2.remaining_quantity == 2
    snapshot = engine.get_book()
    assert snapshot.bids == []
    assert snapshot.asks == [BookLevel(price=100, quantity=2, order_count=1)]

    # Step 5
    cancelled = engine.cancel(2)
    assert cancelled.status is OrderStatus.CANCELLED
    snapshot = engine.get_book()
    assert snapshot.bids == [] and snapshot.asks == []
