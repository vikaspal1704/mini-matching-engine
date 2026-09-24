"""Exception hierarchy for the matching engine."""


class MatchingEngineError(Exception):
    """Base for all engine errors."""


class ValidationError(MatchingEngineError):
    """Invalid arguments (price, qty, side, symbol)."""


class OrderNotFoundError(MatchingEngineError):
    """Unknown order_id."""


class OrderNotCancellableError(MatchingEngineError):
    """Order exists but is FILLED or already CANCELLED."""
