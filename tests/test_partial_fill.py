from matching_engine import BookLevel, OrderSide, OrderStatus


def test_partial_fill_rests_residual(engine):
    engine.submit_limit(OrderSide.SELL, 50, 10)

    result = engine.submit_limit(OrderSide.BUY, 50, 4)

    assert [t.quantity for t in result.trades] == [4]
    assert result.order.status is OrderStatus.FILLED
    sell = engine.get_order(1)
    assert sell.remaining_quantity == 6
    assert sell.status is OrderStatus.PARTIAL
    assert engine.get_book().asks == [BookLevel(price=50, quantity=6, order_count=1)]


def test_aggressor_partial_rests(engine):
    engine.submit_limit(OrderSide.SELL, 50, 3)

    result = engine.submit_limit(OrderSide.BUY, 50, 10)

    assert [t.quantity for t in result.trades] == [3]
    assert result.order.status is OrderStatus.PARTIAL
    assert result.order.remaining_quantity == 7
    snapshot = engine.get_book()
    assert snapshot.bids == [BookLevel(price=50, quantity=7, order_count=1)]
    assert snapshot.asks == []
