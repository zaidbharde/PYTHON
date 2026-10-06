"""Utilities for normalizing and merging inclusive integer intervals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class Interval:
    """An inclusive interval whose start must not exceed its end."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("interval start cannot exceed interval end")

    def touches(self, other: "Interval") -> bool:
        """Return whether intervals overlap or are directly adjacent."""
        return other.start <= self.end + 1 and self.start <= other.end + 1

    def merge(self, other: "Interval") -> "Interval":
        """Return the smallest interval containing both inputs."""
        if not self.touches(other):
            raise ValueError("only touching intervals can be merged")
        return Interval(min(self.start, other.start), max(self.end, other.end))


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[Interval]:
    """Sort intervals and merge overlaps, adjacency, and duplicates."""
    ordered = sorted(Interval(start, end) for start, end in intervals)
    merged: list[Interval] = []
    for current in ordered:
        if merged and merged[-1].touches(current):
            merged[-1] = merged[-1].merge(current)
        else:
            merged.append(current)
    return merged
