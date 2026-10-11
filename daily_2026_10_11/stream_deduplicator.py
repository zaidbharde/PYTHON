"""Bounded time-aware deduplication for event streams."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    key: str
    timestamp: float
    payload: object


class StreamDeduplicator:
    def __init__(self, horizon: float):
        if horizon <= 0:
            raise ValueError("horizon must be positive")
        self.horizon = horizon
        self._seen: dict[str, float] = {}
        self._expiry: deque[tuple[float, str]] = deque()

    def accept(self, event: Event) -> bool:
        """Accept a new key and reject keys seen inside the time horizon."""
        self._expire(event.timestamp)
        previous = self._seen.get(event.key)
        if previous is not None and event.timestamp - previous <= self.horizon:
            return False
        self._seen[event.key] = event.timestamp
        self._expiry.append((event.timestamp + self.horizon, event.key))
        return True

    def _expire(self, now: float) -> None:
        while self._expiry and self._expiry[0][0] < now:
            _, key = self._expiry.popleft()
            timestamp = self._seen.get(key)
            if timestamp is not None and timestamp + self.horizon < now:
                del self._seen[key]

    def active_keys(self) -> set[str]:
        """Return keys currently retained by the deduplicator."""
        return set(self._seen)

    def __len__(self) -> int:
        return len(self._seen)


if __name__ == "__main__":
    dedupe = StreamDeduplicator(10)
    print(dedupe.accept(Event("job-1", 100, "start")))
    print(dedupe.accept(Event("job-1", 105, "retry")))
