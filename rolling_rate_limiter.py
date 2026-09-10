"""Thread-safe rolling-window rate limiter with deterministic pruning."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Lock


@dataclass
class RollingRateLimiter:
    """Allow at most ``limit`` events during the preceding ``window`` seconds."""

    limit: int
    window: float

    def __post_init__(self) -> None:
        if self.limit <= 0 or self.window <= 0:
            raise ValueError("limit and window must be positive")
        self._events: deque[float] = deque()
        self._lock = Lock()

    def _prune(self, now: float) -> None:
        cutoff = now - self.window
        while self._events and self._events[0] <= cutoff:
            self._events.popleft()

    def allow(self, now: float) -> bool:
        """Record an event when capacity exists and return whether it was accepted."""
        with self._lock:
            self._prune(now)
            if len(self._events) >= self.limit:
                return False
            self._events.append(now)
            return True

    def retry_after(self, now: float) -> float:
        """Return seconds until the oldest retained event leaves the window."""
        with self._lock:
            self._prune(now)
            if not self._events:
                return 0.0
            return max(0.0, self._events[0] + self.window - now)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._events)
