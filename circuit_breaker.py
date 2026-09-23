"""Small circuit breaker for protecting unstable downstream calls."""
from dataclasses import dataclass
from time import monotonic
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class CircuitBreaker:
    failure_limit: int = 3
    reset_after: float = 30.0
    failures: int = 0
    opened_at: float | None = None

    def call(self, operation: Callable[[], T]) -> T:
        if self.is_open():
            raise RuntimeError("circuit is open")
        try:
            result = operation()
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_limit:
                self.opened_at = monotonic()
            raise
        self.failures = 0
        self.opened_at = None
        return result

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if monotonic() - self.opened_at >= self.reset_after:
            self.opened_at = None
            self.failures = 0
            return False
        return True
