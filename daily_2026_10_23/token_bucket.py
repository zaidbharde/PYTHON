"""Token-bucket admission control with injectable time for reliable tests."""
from dataclasses import dataclass
from time import monotonic
from typing import Callable


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    clock: Callable[[], float] = monotonic

    def __post_init__(self) -> None:
        if self.capacity <= 0 or self.refill_per_second <= 0:
            raise ValueError("capacity and refill rate must be positive")
        self.tokens = self.capacity
        self._last = self.clock()

    def _refill(self) -> None:
        now = self.clock()
        elapsed = max(0.0, now - self._last)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self._last = now

    def allow(self, cost: float = 1.0) -> bool:
        if cost <= 0 or cost > self.capacity:
            raise ValueError("cost must be positive and fit the bucket")
        self._refill()
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

    def available(self) -> float:
        self._refill()
        return self.tokens


if __name__ == "__main__":
    print(TokenBucket(5, 1).allow())
