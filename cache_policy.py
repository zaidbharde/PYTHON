"""Small thread-safe TTL cache for scripts that need bounded reuse."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """In-memory cache that expires entries after a configurable number of seconds."""

    def __init__(self, ttl_seconds: float) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = ttl_seconds
        self._items: dict[str, _Entry[T]] = {}
        self._lock = RLock()

    def put(self, key: str, value: T) -> None:
        """Store a value and reset its expiration window."""
        with self._lock:
            self._items[key] = _Entry(value, monotonic() + self._ttl)

    def get(self, key: str) -> T | None:
        """Return a live value, removing it when its TTL has elapsed."""
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            if monotonic() >= entry.expires_at:
                self._items.pop(key, None)
                return None
            return entry.value

    def discard_expired(self) -> int:
        """Remove expired entries and return the number deleted."""
        now = monotonic()
        with self._lock:
            expired = [key for key, item in self._items.items() if item.expires_at <= now]
            for key in expired:
                del self._items[key]
            return len(expired)
