"""Merge inclusive intervals and report coverage statistics."""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Coverage:
    intervals: tuple[tuple[int, int], ...]
    covered_points: int
    largest_gap: int


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> Coverage:
    """Normalize, merge, and summarize inclusive integer intervals."""
    normalized = sorted((min(left, right), max(left, right)) for left, right in intervals)
    if not normalized:
        return Coverage((), 0, 0)

    merged: list[list[int]] = []
    for start, end in normalized:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    covered = sum(end - start + 1 for start, end in merged)
    largest_gap = max(
        (next_start - previous_end - 1
         for (_, previous_end), (next_start, _) in zip(merged, merged[1:])),
        default=0,
    )
    return Coverage(tuple(map(tuple, merged)), covered, largest_gap)


if __name__ == "__main__":
    sample = [(8, 10), (1, 3), (3, 5), (14, 12)]
    print(merge_intervals(sample))
