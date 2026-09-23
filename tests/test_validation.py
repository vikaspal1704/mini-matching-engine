import pytest

from matching_engine import MatchingEngine, OrderSide, ValidationError


@pytest.mark.parametrize("price", [0, -1])
def test_reject_non_positive_price(engine, price):
    with pytest.raises(ValidationError):
        engine.submit_limit(OrderSide.BUY, price, 1)

    snapshot = engine.get_book()
    assert snapshot.bids == [] and snapshot.asks == []


@pytest.mark.parametrize("quantity", [0, -5])
def test_reject_non_positive_quantity(engine, quantity):
    with pytest.raises(ValidationError):
        engine.submit_limit(OrderSide.SELL, 100, quantity)

    snapshot = engine.get_book()
    assert snapshot.bids == [] and snapshot.asks == []


@pytest.mark.parametrize("symbol", ["", None, 123])
def test_reject_empty_symbol(symbol):
    with pytest.raises(ValidationError):
        MatchingEngine(symbol)


@pytest.mark.parametrize("side", ["BUY", "buy", None, 1])
def test_reject_invalid_side(engine, side):
    with pytest.raises(ValidationError):
        engine.submit_limit(side, 100, 1)


@pytest.mark.parametrize(
    ("price", "quantity"), [(100.5, 1), (100, 1.0), ("100", 1), (True, 1), (100, True)]
)
def test_reject_non_int_price_or_quantity(engine, price, quantity):
    with pytest.raises(ValidationError):
        engine.submit_limit(OrderSide.BUY, price, quantity)


def test_rejected_submit_does_not_consume_order_id(engine):
    with pytest.raises(ValidationError):
        engine.submit_limit(OrderSide.BUY, 0, 1)

    result = engine.submit_limit(OrderSide.BUY, 100, 1)

    assert result.order.order_id == 1
