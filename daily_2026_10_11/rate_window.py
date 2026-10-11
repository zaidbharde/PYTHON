"""Sliding-window rate calculations for timestamped request events."""
from collections import deque


class RateWindow:
    def __init__(self, duration: float):
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.duration = duration
        self._events: deque[float] = deque()

    def record(self, timestamp: float) -> None:
        """Record an event and discard timestamps outside the current window."""
        if self._events and timestamp < self._events[-1]:
            raise ValueError("timestamps must be non-decreasing")
        self._events.append(timestamp)
        self._expire(timestamp)

    def _expire(self, now: float) -> None:
        cutoff = now - self.duration
        while self._events and self._events[0] <= cutoff:
            self._events.popleft()

    def count(self, now: float) -> int:
        """Return the number of events in the half-open trailing window."""
        self._expire(now)
        return len(self._events)

    def per_second(self, now: float) -> float:
        """Return the current event rate, including zero for an empty window."""
        return self.count(now) / self.duration

    def snapshot(self, now: float) -> dict[str, float | int]:
        """Return compact metrics suitable for a monitoring endpoint."""
        count = self.count(now)
        return {"count": count, "duration": self.duration,
                "rate_per_second": count / self.duration}


if __name__ == "__main__":
    window = RateWindow(5)
    for moment in (1, 2, 4, 7):
        window.record(moment)
    print(window.snapshot(7))
