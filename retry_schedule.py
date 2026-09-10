"""Deterministic exponential retry schedules with jitter-free bounds."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrySchedule:
    attempts: int
    initial_delay: float = 0.5
    multiplier: float = 2.0
    maximum_delay: float = 30.0

    def __post_init__(self) -> None:
        if self.attempts < 0:
            raise ValueError("attempts cannot be negative")
        if self.initial_delay < 0 or self.multiplier < 1:
            raise ValueError("delay must be non-negative and multiplier at least one")
        if self.maximum_delay < self.initial_delay:
            raise ValueError("maximum delay must cover the initial delay")

    def delays(self) -> tuple[float, ...]:
        """Return one capped delay for each retry attempt."""
        result: list[float] = []
        delay = self.initial_delay
        for _ in range(self.attempts):
            result.append(min(delay, self.maximum_delay))
            delay = min(delay * self.multiplier, self.maximum_delay)
        return tuple(result)

    def elapsed_before(self, attempt: int) -> float:
        """Return total waiting time before the requested zero-based attempt."""
        if attempt < 0 or attempt > self.attempts:
            raise IndexError("attempt outside schedule")
        return sum(self.delays()[:attempt])

    def next_deadline(self, started_at: float, attempt: int) -> float:
        """Compute an absolute deadline using the schedule's elapsed offset."""
        return started_at + self.elapsed_before(attempt)
