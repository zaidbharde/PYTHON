from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic


@dataclass
class SlidingWindowLimiter:
    capacity: int
    window_seconds: float

    def __post_init__(self) -> None:
        if self.capacity < 1 or self.window_seconds <= 0:
            raise ValueError("capacity and window must be positive")
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        events = self._events[client]
        cutoff = current - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= self.capacity:
            return False
        events.append(current)
        return True

    def remaining(self, client: str, now: float | None = None) -> int:
        current = monotonic() if now is None else now
        events = self._events[client]
        cutoff = current - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        return max(0, self.capacity - len(events))


if __name__ == "__main__":
    limiter = SlidingWindowLimiter(capacity=2, window_seconds=10)
    print([limiter.allow("demo", now=value) for value in (1.0, 2.0, 3.0)])
    print(limiter.remaining("demo", now=12.0))
