import pytest

from matching_engine import MatchingEngine


@pytest.fixture
def engine() -> MatchingEngine:
    return MatchingEngine("DEMO")
