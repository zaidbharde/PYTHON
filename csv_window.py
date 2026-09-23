"""Streaming CSV window aggregation without loading the whole file."""
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class WindowTotal:
    key: str
    total: float
    count: int


def rolling_totals(rows: Iterable[tuple[str, float]], width: int) -> Iterator[WindowTotal]:
    if width <= 0:
        raise ValueError("width must be positive")
    windows: dict[str, deque[float]] = {}
    sums: dict[str, float] = {}
    for key, value in rows:
        bucket = windows.setdefault(key, deque())
        bucket.append(float(value))
        sums[key] = sums.get(key, 0.0) + float(value)
        if len(bucket) > width:
            sums[key] -= bucket.popleft()
        yield WindowTotal(key, sums[key], len(bucket))


def parse_rows(lines: Iterable[str]) -> Iterator[tuple[str, float]]:
    for line_number, line in enumerate(lines, 1):
        raw = line.strip()
        if not raw:
            continue
        parts = raw.split(",")
        if len(parts) != 2:
            raise ValueError(f"line {line_number}: expected key,value")
        try:
            yield parts[0].strip(), float(parts[1])
        except ValueError as exc:
            raise ValueError(f"line {line_number}: value is not numeric") from exc
