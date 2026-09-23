"""Demo: replay the canonical worked example (docs/ARCHITECTURE.md §7).

Run with ``python -m demo.cli``. Uses only the public ``matching_engine`` API.
"""

from matching_engine import MatchingEngine, OrderBookSnapshot, OrderSide, Trade


def format_trade(trade: Trade) -> str:
    return (
        f"  TRADE #{trade.trade_id}: {trade.quantity} @ {trade.price} "
        f"(buy #{trade.buy_order_id} / sell #{trade.sell_order_id})"
    )


def format_book(snapshot: OrderBookSnapshot) -> str:
    lines = [f"Book [{snapshot.symbol}]", "  ASKS"]
    lines += [
        f"    {level.price:>6} x {level.quantity:<6} ({level.order_count} orders)"
        for level in reversed(snapshot.asks)
    ] or ["    (empty)"]
    lines.append("  BIDS")
    lines += [
        f"    {level.price:>6} x {level.quantity:<6} ({level.order_count} orders)"
        for level in snapshot.bids
    ] or ["    (empty)"]
    return "\n".join(lines)


def main() -> None:
    engine = MatchingEngine("DEMO")
    steps = [
        (OrderSide.SELL, 100, 10),
        (OrderSide.SELL, 100, 5),
        (OrderSide.BUY, 101, 3),
        (OrderSide.BUY, 100, 10),
    ]

    for side, price, quantity in steps:
        result = engine.submit_limit(side, price, quantity)
        order = result.order
        print(
            f"SUBMIT {side.value} {quantity} @ {price} -> order #{order.order_id} "
            f"{order.status.value} (remaining {order.remaining_quantity})"
        )
        for trade in result.trades:
            print(format_trade(trade))

    print()
    print(format_book(engine.get_book()))

    cancelled = engine.cancel(2)
    print()
    print(f"CANCEL order #{cancelled.order_id} -> {cancelled.status.value}")
    print(format_book(engine.get_book()))


if __name__ == "__main__":
    main()
