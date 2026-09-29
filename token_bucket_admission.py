"""A small monotonic token bucket suitable for rate-limit decisions."""

from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    tokens: float | None = None
    last_time: float = 0.0

    def __post_init__(self) -> None:
        if self.capacity <= 0 or self.refill_per_second < 0:
            raise ValueError("capacity must be positive and refill rate non-negative")
        if self.tokens is None:
            self.tokens = self.capacity
        self.tokens = min(self.capacity, max(0.0, self.tokens))

    def allow(self, cost: float, now: float) -> bool:
        """Consume cost if enough tokens exist at the supplied monotonic time."""
        if cost < 0 or now < self.last_time:
            raise ValueError("cost must be non-negative and time cannot move backward")
        elapsed = now - self.last_time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.last_time = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True
