from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    _tokens: float = field(init=False)
    _updated_at: float = field(default_factory=time.monotonic, init=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.capacity <= 0 or self.refill_per_second <= 0:
            raise ValueError("capacity and refill rate must be positive")
        self._tokens = self.capacity

    def allow(self, cost: float = 1.0) -> bool:
        if cost <= 0 or cost > self.capacity:
            raise ValueError("cost must fit within the bucket")
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._updated_at
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_second)
            self._updated_at = now
            if self._tokens < cost:
                return False
            self._tokens -= cost
            return True

    def wait_time(self, cost: float = 1.0) -> float:
        if cost <= 0 or cost > self.capacity:
            raise ValueError("cost must fit within the bucket")
        with self._lock:
            deficit = max(0.0, cost - self._tokens)
            return deficit / self.refill_per_second


if __name__ == "__main__":
    limiter = TokenBucket(capacity=3, refill_per_second=2)
    print([limiter.allow() for _ in range(5)])
