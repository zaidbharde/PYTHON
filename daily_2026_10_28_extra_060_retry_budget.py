"""A shared finite retry allowance that refills only when explicitly requested."""
from threading import Lock


class RetryBudget:
    """Thread-safe retry tokens with a fixed capacity and explicit refills."""

    def __init__(self, capacity: int, initial: int | None = None) -> None:
        self._require_count(capacity, "capacity")
        if capacity == 0:
            raise ValueError("capacity must be positive")
        initial = capacity if initial is None else initial
        self._require_count(initial, "initial")
        if initial > capacity:
            raise ValueError("initial cannot exceed capacity")
        self._capacity = capacity
        self._remaining = initial
        self._lock = Lock()

    @staticmethod
    def _require_count(value: int, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    @property
    def remaining(self) -> int:
        """Current number of available retries."""
        with self._lock:
            return self._remaining

    @property
    def capacity(self) -> int:
        return self._capacity

    def consume(self, count: int = 1) -> bool:
        """Atomically spend count retries; leave state unchanged if insufficient."""
        self._require_count(count, "count")
        with self._lock:
            if count > self._remaining:
                return False
            self._remaining -= count
            return True

    def refill(self, count: int) -> int:
        """Add up to count retries, capped at capacity; return the amount added."""
        self._require_count(count, "count")
        with self._lock:
            added = min(count, self._capacity - self._remaining)
            self._remaining += added
            return added


if __name__ == "__main__":
    budget = RetryBudget(3, initial=1)
    assert budget.consume()
    assert not budget.consume()
    assert budget.remaining == 0
    assert budget.refill(2) == 2
    assert budget.consume(2)
    assert budget.refill(5) == 3
    assert budget.remaining == budget.capacity == 3
    for invalid in (-1, True, 1.5):
        try:
            budget.refill(invalid)  # type: ignore[arg-type]
        except ValueError:
            pass
        else:
            raise AssertionError("invalid refill count accepted")
