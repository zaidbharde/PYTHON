"""Count keyed events inside a moving time window without external dependencies."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    timestamp: float
    key: str


class LogWindowCounter:
    def __init__(self, width_seconds: float) -> None:
        if width_seconds <= 0:
            raise ValueError("window width must be positive")
        self.width = width_seconds
        self._events: deque[Event] = deque()
        self._counts: dict[str, int] = defaultdict(int)
        self._latest = float("-inf")

    def add(self, timestamp: float, key: str) -> None:
        if timestamp < self._latest:
            raise ValueError("events must arrive in nondecreasing order")
        self._latest = timestamp
        event = Event(timestamp, key)
        self._events.append(event)
        self._counts[key] += 1
        self._expire(timestamp)

    def _expire(self, now: float) -> None:
        cutoff = now - self.width
        while self._events and self._events[0].timestamp <= cutoff:
            expired = self._events.popleft()
            self._counts[expired.key] -= 1
            if self._counts[expired.key] == 0:
                del self._counts[expired.key]

    def count(self, key: str, now: float | None = None) -> int:
        if now is not None:
            if now < self._latest:
                raise ValueError("query time cannot move backwards")
            self._latest = now
            self._expire(now)
        return self._counts.get(key, 0)

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self._counts.items()))


if __name__ == "__main__":
    counter = LogWindowCounter(10)
    for stamp, key in [(1, "api"), (4, "worker"), (8, "api"), (12, "api")]:
        counter.add(stamp, key)
    print(counter.snapshot())
