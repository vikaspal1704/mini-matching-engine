import pytest

from matching_engine import (
    BookLevel,
    MatchingEngine,
    OrderNotFoundError,
    OrderSide,
    OrderStatus,
)


def test_get_book_sorted_levels(engine):
    engine.submit_limit(OrderSide.BUY, 99, 1)
    engine.submit_limit(OrderSide.BUY, 100, 1)
    engine.submit_limit(OrderSide.SELL, 102, 1)
    engine.submit_limit(OrderSide.SELL, 101, 1)

    snapshot = engine.get_book()

    assert [level.price for level in snapshot.bids] == [100, 99]
    assert [level.price for level in snapshot.asks] == [101, 102]


def test_book_aggregates_same_price(engine):
    engine.submit_limit(OrderSide.BUY, 100, 3)
    engine.submit_limit(OrderSide.BUY, 100, 7)

    assert engine.get_book().bids == [BookLevel(price=100, quantity=10, order_count=2)]


def test_get_book_empty(engine):
    snapshot = engine.get_book()

    assert snapshot.symbol == "DEMO"
    assert snapshot.bids == [] and snapshot.asks == []


def test_get_order_states(engine):
    engine.submit_limit(OrderSide.SELL, 100, 10)
    assert engine.get_order(1).status is OrderStatus.OPEN

    engine.submit_limit(OrderSide.BUY, 100, 4)
    assert engine.get_order(1).status is OrderStatus.PARTIAL
    assert engine.get_order(1).remaining_quantity == 6

    engine.submit_limit(OrderSide.BUY, 100, 6)
    order = engine.get_order(1)
    assert order.status is OrderStatus.FILLED
    assert order.remaining_quantity == 0
    assert order.original_quantity == 10


def test_get_order_not_found(engine):
    with pytest.raises(OrderNotFoundError):
        engine.get_order(1)


def test_get_order_returns_copy(engine):
    engine.submit_limit(OrderSide.BUY, 100, 10)

    engine.get_order(1).remaining_quantity = 0

    assert engine.get_order(1).remaining_quantity == 10
    assert engine.get_book().bids[0].quantity == 10


def test_order_ids_monotonic_unique(engine):
    ids = [engine.submit_limit(OrderSide.BUY, 100 + i, 1).order.order_id for i in range(5)]

    assert ids == [1, 2, 3, 4, 5]


def test_trade_ids_monotonic(engine):
    engine.submit_limit(OrderSide.SELL, 100, 1)
    engine.submit_limit(OrderSide.SELL, 101, 1)
    engine.submit_limit(OrderSide.SELL, 102, 1)

    first = engine.submit_limit(OrderSide.BUY, 101, 2).trades
    second = engine.submit_limit(OrderSide.BUY, 102, 1).trades

    assert [t.trade_id for t in first + second] == [1, 2, 3]


def test_symbol_echoed_on_order_and_trade():
    engine = MatchingEngine("ABC")
    engine.submit_limit(OrderSide.SELL, 100, 1)

    result = engine.submit_limit(OrderSide.BUY, 100, 1)

    assert result.order.symbol == "ABC"
    assert result.trades[0].symbol == "ABC"
    assert engine.get_order(1).symbol == "ABC"
    assert engine.get_book().symbol == "ABC"


def test_client_order_id_round_trip(engine):
    result = engine.submit_limit(OrderSide.BUY, 100, 1, client_order_id="abc-1")

    assert result.order.client_order_id == "abc-1"
    assert engine.get_order(1).client_order_id == "abc-1"
