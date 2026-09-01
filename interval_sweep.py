"""Interval normalization helpers for schedules, reservations, and telemetry spans."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class Interval:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("interval end must not precede start")

    @property
    def duration(self) -> int:
        return self.end - self.start


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    ordered = sorted(intervals, key=lambda item: (item.start, item.end))
    merged: list[Interval] = []
    for current in ordered:
        if not merged or current.start > merged[-1].end:
            merged.append(current)
            continue
        previous = merged[-1]
        merged[-1] = Interval(previous.start, max(previous.end, current.end))
    return merged


def covered_duration(intervals: Iterable[Interval]) -> int:
    return sum(item.duration for item in merge_intervals(intervals))


if __name__ == "__main__":
    sample = [Interval(1, 4), Interval(3, 8), Interval(10, 12)]
    print(merge_intervals(sample), covered_duration(sample))
