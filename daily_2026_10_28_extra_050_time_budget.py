"""Context manager for checking whether a monotonic time budget expired."""
from __future__ import annotations

from math import isfinite
from time import monotonic
from typing import Callable


class TimeBudget:
    """Track a duration from context entry and expose its expiration state."""

    def __init__(self, seconds: float, clock: Callable[[], float] = monotonic) -> None:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise TypeError("seconds must be a finite number")
        if not isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be finite and non-negative")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self.seconds = float(seconds)
        self._clock = clock
        self._deadline: float | None = None
        self._expired = False
        self._active = False

    def __enter__(self) -> TimeBudget:
        if self._active or self._deadline is not None:
            raise RuntimeError("TimeBudget instances cannot be reused")
        self._deadline = self._read_clock() + self.seconds
        self._active = True
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self._expired = self.expired
        self._active = False
        return False

    @property
    def expired(self) -> bool:
        """Whether the deadline has passed, including during the context."""
        if self._deadline is None:
            raise RuntimeError("TimeBudget must be entered before checking expiration")
        if self._active:
            self._expired = self._expired or self._read_clock() >= self._deadline
        return self._expired

    def _read_clock(self) -> float:
        value = self._clock()
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("clock must return a finite number")
        return float(value)


if __name__ == "__main__":
    ticks = iter((10.0, 10.4, 11.0, 11.0))
    with TimeBudget(1.0, lambda: next(ticks)) as budget:
        assert not budget.expired
        assert budget.expired
    assert budget.expired
    try:
        TimeBudget(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative budgets must be rejected")
    print("TimeBudget self-check passed")
