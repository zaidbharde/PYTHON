"""Build retry times for jobs while enforcing a finite attempt budget."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


@dataclass(frozen=True)
class Retry:
    attempt: int
    when: datetime
    delay_seconds: int


def retries(start: datetime, attempts: int, base_seconds: int = 5, cap_seconds: int = 300) -> list[Retry]:
    """Return exponential-backoff retry times, excluding the initial attempt."""
    if attempts < 0 or base_seconds <= 0 or cap_seconds < base_seconds:
        raise ValueError("invalid retry policy")
    result: list[Retry] = []
    current = start
    for attempt in range(1, attempts + 1):
        delay = min(cap_seconds, base_seconds * (2 ** (attempt - 1)))
        current += timedelta(seconds=delay)
        result.append(Retry(attempt, current, delay))
    return result


def pending_retries(start: datetime, completed: Iterable[int], attempts: int) -> list[Retry]:
    """Filter a retry plan to attempts that have not already completed."""
    done = set(completed)
    return [item for item in retries(start, attempts) if item.attempt not in done]


if __name__ == "__main__":
    print(retries(datetime(2026, 1, 1), 3))
