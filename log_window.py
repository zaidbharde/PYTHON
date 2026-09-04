"""Aggregate timestamped log events into fixed-width windows."""
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Event:
    timestamp: datetime
    level: str
    message: str


class WindowCounter:
    def __init__(self, width_seconds: int) -> None:
        if width_seconds <= 0:
            raise ValueError("window width must be positive")
        self.width = width_seconds
        self._events: deque[Event] = deque()
        self._levels: Counter[str] = Counter()

    def add(self, event: Event) -> None:
        self._events.append(event)
        self._levels[event.level] += 1
        self._discard_before(event.timestamp.timestamp() - self.width)

    def snapshot(self, now: datetime) -> dict[str, int]:
        self._discard_before(now.timestamp() - self.width)
        return dict(self._levels)

    def _discard_before(self, cutoff: float) -> None:
        while self._events and self._events[0].timestamp.timestamp() < cutoff:
            expired = self._events.popleft()
            self._levels[expired.level] -= 1
            if self._levels[expired.level] == 0:
                del self._levels[expired.level]


def parse_event(line: str) -> Event:
    timestamp, level, message = line.rstrip("\n").split(" ", 2)
    return Event(datetime.fromisoformat(timestamp), level.upper(), message)
