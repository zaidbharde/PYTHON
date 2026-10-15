"""Group timestamped events into fixed-width calendar buckets."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import TypeVar

T = TypeVar("T")


def bucket_events(events: Iterable[tuple[datetime, T]], width: timedelta) -> dict[datetime, list[T]]:
    """Return events keyed by the start of their containing bucket."""
    if width <= timedelta(0):
        raise ValueError("width must be positive")
    result: dict[datetime, list[T]] = {}
    for timestamp, value in events:
        epoch = datetime.min.replace(tzinfo=timestamp.tzinfo)
        elapsed = timestamp - epoch
        bucket_count = elapsed // width
        start = epoch + bucket_count * width
        result.setdefault(start, []).append(value)
    return dict(sorted(result.items()))


def bucket_counts(events: Iterable[datetime], width: timedelta) -> dict[datetime, int]:
    """Count timestamps without retaining their payloads."""
    grouped = bucket_events(((stamp, 1) for stamp in events), width)
    return {start: len(values) for start, values in grouped.items()}


if __name__ == "__main__":
    now = datetime(2026, 1, 1, 12, 0)
    sample = [(now + timedelta(minutes=i), i) for i in (0, 7, 18)]
    print(bucket_events(sample, timedelta(minutes=15)))
