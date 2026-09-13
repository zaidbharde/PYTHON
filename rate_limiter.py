"""Thread-safe sliding-window rate limiter for small synchronous services."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from time import monotonic


@dataclass
class SlidingWindowLimiter:
    """Allow at most ``limit`` calls during each rolling time window."""

    limit: int
    window_seconds: float
    _events: deque[float] = field(default_factory=deque, init=False)
    _lock: Lock = field(default_factory=Lock, init=False)

    def __post_init__(self) -> None:
        if self.limit <= 0 or self.window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")

    def allow(self, now: float | None = None) -> bool:
        """Record a request when capacity exists and return whether it passed."""
        timestamp = monotonic() if now is None else now
        cutoff = timestamp - self.window_seconds
        with self._lock:
            while self._events and self._events[0] <= cutoff:
                self._events.popleft()
            if len(self._events) >= self.limit:
                return False
            self._events.append(timestamp)
            return True

    def retry_after(self, now: float | None = None) -> float:
        """Return seconds until the oldest event leaves the window."""
        timestamp = monotonic() if now is None else now
        with self._lock:
            if len(self._events) < self.limit:
                return 0.0
            return max(0.0, self._events[0] + self.window_seconds - timestamp)
