from matching_engine import BookLevel, OrderSide, OrderStatus


def test_submit_buy_and_sell_rest(engine):
    buy = engine.submit_limit(OrderSide.BUY, 100, 10)
    sell = engine.submit_limit(OrderSide.SELL, 101, 5)

    assert buy.trades == [] and sell.trades == []
    assert buy.order.status is OrderStatus.OPEN
    assert sell.order.status is OrderStatus.OPEN
    snapshot = engine.get_book()
    assert snapshot.bids == [BookLevel(price=100, quantity=10, order_count=1)]
    assert snapshot.asks == [BookLevel(price=101, quantity=5, order_count=1)]


def test_trade_uses_resting_price(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)

    result = engine.submit_limit(OrderSide.BUY, 105, 5)

    assert len(result.trades) == 1
    assert result.trades[0].price == 100


def test_trade_uses_resting_price_for_sell_aggressor(engine):
    engine.submit_limit(OrderSide.BUY, 105, 5)

    result = engine.submit_limit(OrderSide.SELL, 100, 5)

    assert [t.price for t in result.trades] == [105]
    assert result.trades[0].buy_order_id == 1
    assert result.trades[0].sell_order_id == 2


def test_multi_trade_single_submit(engine):
    engine.submit_limit(OrderSide.SELL, 100, 2)
    engine.submit_limit(OrderSide.SELL, 101, 3)
    engine.submit_limit(OrderSide.SELL, 102, 4)

    result = engine.submit_limit(OrderSide.BUY, 102, 9)

    assert len(result.trades) >= 2
    assert [(t.price, t.quantity) for t in result.trades] == [(100, 2), (101, 3), (102, 4)]
    assert result.order.status is OrderStatus.FILLED
    assert engine.get_book().asks == []


def test_no_match_when_buy_below_ask(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)

    result = engine.submit_limit(OrderSide.BUY, 99, 5)

    assert result.trades == []
    snapshot = engine.get_book()
    assert snapshot.bids == [BookLevel(price=99, quantity=5, order_count=1)]
    assert snapshot.asks == [BookLevel(price=100, quantity=5, order_count=1)]


def test_exact_quantity_match_clears_level(engine):
    engine.submit_limit(OrderSide.SELL, 100, 5)

    engine.submit_limit(OrderSide.BUY, 100, 5)

    snapshot = engine.get_book()
    assert snapshot.bids == [] and snapshot.asks == []


def test_sweep_entire_ask_side_rests_residual(engine):
    engine.submit_limit(OrderSide.SELL, 100, 2)
    engine.submit_limit(OrderSide.SELL, 101, 2)

    result = engine.submit_limit(OrderSide.BUY, 105, 10)

    assert sum(t.quantity for t in result.trades) == 4
    assert result.order.status is OrderStatus.PARTIAL
    assert result.order.remaining_quantity == 6
    snapshot = engine.get_book()
    assert snapshot.asks == []
    assert snapshot.bids == [BookLevel(price=105, quantity=6, order_count=1)]


def test_large_sweep_conserves_quantity(engine):
    for price in range(100, 120):
        engine.submit_limit(OrderSide.SELL, price, 3)

    result = engine.submit_limit(OrderSide.BUY, 110, 50)

    filled = result.order.original_quantity - result.order.remaining_quantity
    assert sum(t.quantity for t in result.trades) == filled == 33
    assert all(t.price <= 110 for t in result.trades)


def test_book_not_crossed_after_submit(engine):
    sequence = [
        (OrderSide.BUY, 100, 5),
        (OrderSide.SELL, 103, 4),
        (OrderSide.BUY, 101, 2),
        (OrderSide.SELL, 100, 6),
        (OrderSide.BUY, 104, 3),
        (OrderSide.SELL, 102, 7),
        (OrderSide.BUY, 102, 1),
        (OrderSide.SELL, 99, 10),
        (OrderSide.BUY, 98, 4),
        (OrderSide.SELL, 101, 2),
    ]

    for side, price, quantity in sequence:
        engine.submit_limit(side, price, quantity)
        snapshot = engine.get_book()
        if snapshot.bids and snapshot.asks:
            assert snapshot.bids[0].price < snapshot.asks[0].price


def test_trade_sides_and_quantity_conservation(engine):
    sequence = [
        (OrderSide.SELL, 100, 5),
        (OrderSide.BUY, 101, 3),
        (OrderSide.BUY, 99, 4),
        (OrderSide.SELL, 98, 8),
        (OrderSide.BUY, 100, 6),
    ]
    trades = []
    for side, price, quantity in sequence:
        trades.extend(engine.submit_limit(side, price, quantity).trades)

    for order_id in range(1, len(sequence) + 1):
        order = engine.get_order(order_id)
        own = [t for t in trades if order_id in (t.buy_order_id, t.sell_order_id)]
        assert sum(t.quantity for t in own) == order.original_quantity - order.remaining_quantity
    for trade in trades:
        assert engine.get_order(trade.buy_order_id).side is OrderSide.BUY
        assert engine.get_order(trade.sell_order_id).side is OrderSide.SELL


def test_deterministic_across_fresh_engines():
    from matching_engine import MatchingEngine

    def run():
        engine = MatchingEngine("DEMO")
        trades = []
        for side, price, quantity in [
            (OrderSide.SELL, 100, 5),
            (OrderSide.SELL, 101, 5),
            (OrderSide.BUY, 101, 7),
            (OrderSide.BUY, 99, 2),
        ]:
            trades.extend(engine.submit_limit(side, price, quantity).trades)
        return trades, engine.get_book()

    assert run() == run()
