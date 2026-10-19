"""Summarize maximal monotonic runs in a sequence of comparable values."""

from __future__ import annotations


def monotonic_segments(values: list[int]) -> list[tuple[int, int, str]]:
    if not values:
        return []
    segments: list[tuple[int, int, str]] = []
    start = 0
    direction: str | None = None
    for index in range(1, len(values)):
        step = "up" if values[index] > values[index - 1] else "down" if values[index] < values[index - 1] else "flat"
        if direction is None:
            direction = step
        elif step != direction and step != "flat":
            segments.append((start, index - 1, direction))
            start, direction = index - 1, step
    segments.append((start, len(values) - 1, direction or "flat"))
    return segments


def segment_values(values: list[int]) -> list[list[int]]:
    return [values[start : end + 1] for start, end, _ in monotonic_segments(values)]


if __name__ == "__main__":
    sample = [1, 3, 5, 4, 2, 2, 6]
    print(list(zip(monotonic_segments(sample), segment_values(sample))))
