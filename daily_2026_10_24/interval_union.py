"""Merge inclusive integer intervals and expose uncovered gaps."""
from __future__ import annotations

from typing import Iterable


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted, coalesced intervals while rejecting reversed bounds."""
    ordered = sorted(intervals)
    if any(start > end for start, end in ordered):
        raise ValueError("interval start cannot exceed its end")
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if not merged or start > merged[-1][1] + 1:
            merged.append((start, end))
        else:
            previous_start, previous_end = merged[-1]
            merged[-1] = (previous_start, max(previous_end, end))
    return merged


def uncovered_gaps(
    intervals: Iterable[tuple[int, int]], lower: int, upper: int
) -> list[tuple[int, int]]:
    """Find inclusive gaps inside the requested closed domain."""
    if lower > upper:
        raise ValueError("lower bound cannot exceed upper bound")
    clipped = []
    for start, end in intervals:
        if end >= lower and start <= upper:
            clipped.append((max(start, lower), min(end, upper)))
    covered = merge_intervals(clipped)
    gaps: list[tuple[int, int]] = []
    cursor = lower
    for start, end in covered:
        if cursor < start:
            gaps.append((cursor, start - 1))
        cursor = max(cursor, end + 1)
    if cursor <= upper:
        gaps.append((cursor, upper))
    return gaps


if __name__ == "__main__":
    sample = [(8, 10), (1, 3), (3, 5), (15, 18)]
    assert merge_intervals(sample) == [(1, 5), (8, 10), (15, 18)]
    assert uncovered_gaps(sample, 1, 18) == [(6, 7), (11, 14)]
    print("interval union checks passed")
