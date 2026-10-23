"""Interval utilities for finding free windows in a bounded schedule."""
from collections.abc import Iterable


def merged(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    ordered = sorted(intervals)
    result: list[tuple[int, int]] = []
    for start, end in ordered:
        if start > end:
            raise ValueError("interval start exceeds end")
        if not result or start > result[-1][1]:
            result.append((start, end))
        else:
            result[-1] = (result[-1][0], max(result[-1][1], end))
    return result


def first_gap(intervals: Iterable[tuple[int, int]], window: tuple[int, int]) -> tuple[int, int] | None:
    """Find the earliest non-empty free segment inside ``window``."""
    left, right = window
    if left > right:
        raise ValueError("window start exceeds end")
    cursor = left
    for start, end in merged(intervals):
        if end <= left or start >= right:
            continue
        start, end = max(start, left), min(end, right)
        if start > cursor:
            return cursor, start
        cursor = max(cursor, end)
        if cursor >= right:
            return None
    return (cursor, right) if cursor < right else None


if __name__ == "__main__":
    print(first_gap([(2, 4), (6, 8)], (0, 10)))
