"""Utilities for normalizing intervals and computing covered length."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class Interval:
    start: float
    end: float

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("interval end cannot precede its start")

    @property
    def length(self) -> float:
        return self.end - self.start


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    """Merge overlapping or touching intervals in ascending order."""
    ordered = sorted(intervals, key=lambda item: (item.start, item.end))
    merged: list[Interval] = []
    for current in ordered:
        if not merged or current.start > merged[-1].end:
            merged.append(current)
            continue
        previous = merged[-1]
        merged[-1] = Interval(previous.start, max(previous.end, current.end))
    return merged


def covered_length(intervals: Iterable[Interval]) -> float:
    """Return the measure of the union, counting overlaps only once."""
    return sum(interval.length for interval in merge_intervals(intervals))
