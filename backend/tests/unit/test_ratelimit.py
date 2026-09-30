"""Tests del limitador y del presupuesto diario (T4.2)."""

import pytest

from app.core.ratelimit import (
    DailyBudget,
    RateLimit,
    SlidingWindowLimiter,
    parse_limits,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_parse_limits() -> None:
    limits = parse_limits("10/minute;60/hour")

    assert limits == (RateLimit(10, 60.0), RateLimit(60, 3600.0))


def test_parse_limits_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError):
        parse_limits("10/fortnight")


def test_sliding_window_allows_until_limit_then_retry_after() -> None:
    clock = FakeClock()
    limiter = SlidingWindowLimiter(parse_limits("2/minute"), clock=clock)

    assert limiter.check("ip") is None
    assert limiter.check("ip") is None
    assert limiter.check("ip") == 60

    clock.advance(30)
    assert limiter.check("ip") == 30


def test_sliding_window_separates_keys() -> None:
    clock = FakeClock()
    limiter = SlidingWindowLimiter(parse_limits("1/minute"), clock=clock)

    assert limiter.check("a") is None
    assert limiter.check("b") is None
    assert limiter.check("a") == 60


def test_sliding_window_recovers_after_window() -> None:
    clock = FakeClock()
    limiter = SlidingWindowLimiter(parse_limits("1/minute"), clock=clock)

    assert limiter.check("ip") is None
    assert limiter.check("ip") is not None

    clock.advance(61)
    assert limiter.check("ip") is None


def test_daily_budget_resets_per_day() -> None:
    now = [86400.0 * 20000]
    budget = DailyBudget(1, clock=lambda: now[0])

    assert budget.allow()
    assert not budget.allow()

    now[0] += 86400
    assert budget.allow()


def test_daily_budget_zero_means_unlimited() -> None:
    budget = DailyBudget(0)

    assert all(budget.allow() for _ in range(1000))


def test_daily_budget_negative_means_unlimited() -> None:
    budget = DailyBudget(-5)

    assert budget.allow()
