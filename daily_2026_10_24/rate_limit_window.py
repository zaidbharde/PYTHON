"""A deterministic sliding-window limiter for timestamped requests."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class SlidingWindow:
    """Allow at most limit events during any width-second window."""

    limit: int
    width: float
    _events: deque[float] = field(default_factory=deque)

    def __post_init__(self) -> None:
        if self.limit <= 0 or self.width <= 0:
            raise ValueError("limit and width must be positive")

    def allow(self, timestamp: float) -> bool:
        """Record timestamp when capacity exists and return the decision."""
        self._expire(timestamp)
        if len(self._events) >= self.limit:
            return False
        self._events.append(timestamp)
        return True

    def retry_after(self, timestamp: float) -> float:
        """Return seconds until a rejected request can be admitted."""
        self._expire(timestamp)
        if len(self._events) < self.limit:
            return 0.0
        return max(0.0, self._events[0] + self.width - timestamp)

    def _expire(self, timestamp: float) -> None:
        cutoff = timestamp - self.width
        while self._events and self._events[0] <= cutoff:
            self._events.popleft()

    @property
    def pending(self) -> tuple[float, ...]:
        """Expose an immutable snapshot for metrics and tests."""
        return tuple(self._events)


if __name__ == "__main__":
    limiter = SlidingWindow(limit=2, width=10)
    assert limiter.allow(1.0)
    assert limiter.allow(2.0)
    assert not limiter.allow(3.0)
    assert limiter.retry_after(3.0) == 8.0
    assert limiter.allow(11.0)
    print("sliding window checks passed")
