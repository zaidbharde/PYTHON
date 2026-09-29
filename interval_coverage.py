"""Compute merged interval coverage and uncovered gaps."""

from collections.abc import Iterable


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge half-open integer intervals and reject inverted ranges."""
    ordered = sorted(intervals)
    if any(start > end for start, end in ordered):
        raise ValueError("interval start cannot exceed its end")
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            old_start, old_end = merged[-1]
            merged[-1] = (old_start, max(old_end, end))
    return merged


def uncovered_gaps(
    intervals: Iterable[tuple[int, int]], lower: int, upper: int
) -> list[tuple[int, int]]:
    """Return gaps inside [lower, upper) after clipping interval coverage."""
    if lower > upper:
        raise ValueError("lower bound cannot exceed upper bound")
    clipped = [(max(lower, a), min(upper, b)) for a, b in intervals]
    cursor = lower
    gaps: list[tuple[int, int]] = []
    for start, end in merge_intervals((a, b) for a, b in clipped if a < b):
        if cursor < start:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < upper:
        gaps.append((cursor, upper))
    return gaps
