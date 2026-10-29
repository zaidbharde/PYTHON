"""Deterministic token bucket for fractional costs and caller-supplied timestamps."""
from __future__ import annotations

from dataclasses import dataclass, field
import math


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


@dataclass
class TokenBucketFloat:
    """A token bucket advanced only by explicit, nondecreasing ``now`` values."""
    capacity: float
    refill_per_second: float
    start_time: float = 0.0
    tokens: float = field(init=False)
    _last_time: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.capacity = _finite(self.capacity, "capacity")
        self.refill_per_second = _finite(self.refill_per_second, "refill_per_second")
        self.start_time = _finite(self.start_time, "start_time")
        if self.capacity <= 0 or self.refill_per_second < 0:
            raise ValueError("capacity must be positive and refill rate non-negative")
        self.tokens = self.capacity
        self._last_time = self.start_time

    def _advance(self, now: float) -> None:
        now = _finite(now, "now")
        if now < self._last_time:
            raise ValueError("time cannot move backward")
        self.tokens = min(self.capacity, self.tokens + (now - self._last_time) * self.refill_per_second)
        self._last_time = now

    def consume(self, cost: float, now: float) -> bool:
        """Advance to ``now`` and consume positive fractional ``cost`` if available."""
        cost = _finite(cost, "cost")
        if not 0 < cost <= self.capacity:
            raise ValueError("cost must be positive and no greater than capacity")
        self._advance(now)
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

    def available(self, now: float) -> float:
        """Return the refilled balance at the supplied timestamp."""
        self._advance(now)
        return self.tokens


if __name__ == "__main__":
    bucket = TokenBucketFloat(capacity=2.5, refill_per_second=0.5)
    assert bucket.consume(1.25, 0.0)
    assert bucket.available(1.0) == 1.75
    assert bucket.consume(1.75, 1.0)
    assert not bucket.consume(0.1, 1.0)
    assert bucket.available(3.0) == 1.0
    try:
        bucket.available(2.0)
    except ValueError:
        pass
    else:
        raise AssertionError("backward time must be rejected")
