from matching_engine import OrderSide, OrderStatus


def test_time_priority_same_price(engine):
    engine.submit_limit(OrderSide.SELL, 100, 10)
    engine.submit_limit(OrderSide.SELL, 100, 5)

    result = engine.submit_limit(OrderSide.BUY, 100, 12)

    assert [(t.sell_order_id, t.quantity, t.price) for t in result.trades] == [
        (1, 10, 100),
        (2, 2, 100),
    ]
    assert engine.get_order(1).status is OrderStatus.FILLED
    order_2 = engine.get_order(2)
    assert order_2.status is OrderStatus.PARTIAL
    assert order_2.remaining_quantity == 3
    assert result.order.status is OrderStatus.FILLED


def test_price_priority_across_levels(engine):
    engine.submit_limit(OrderSide.SELL, 99, 4)
    engine.submit_limit(OrderSide.SELL, 100, 4)

    result = engine.submit_limit(OrderSide.BUY, 100, 6)

    assert [(t.sell_order_id, t.price, t.quantity) for t in result.trades] == [
        (1, 99, 4),
        (2, 100, 2),
    ]
    assert result.order.status is OrderStatus.FILLED
    assert engine.get_order(2).remaining_quantity == 2


def test_price_priority_for_sell_aggressor(engine):
    engine.submit_limit(OrderSide.BUY, 100, 4)
    engine.submit_limit(OrderSide.BUY, 101, 4)

    result = engine.submit_limit(OrderSide.SELL, 100, 6)

    assert [(t.buy_order_id, t.price, t.quantity) for t in result.trades] == [
        (2, 101, 4),
        (1, 100, 2),
    ]


def test_cancel_head_of_fifo_then_match(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)
    engine.submit_limit(OrderSide.SELL, 100, 5)
    engine.cancel(1)

    result = engine.submit_limit(OrderSide.BUY, 100, 3)

    assert [t.sell_order_id for t in result.trades] == [2]


def test_cancel_middle_of_fifo_keeps_relative_order(engine):
    for _ in range(3):
        engine.submit_limit(OrderSide.SELL, 100, 2)
    engine.cancel(2)

    result = engine.submit_limit(OrderSide.BUY, 100, 4)

    assert [t.sell_order_id for t in result.trades] == [1, 3]
