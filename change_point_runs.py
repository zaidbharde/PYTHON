"""Find maximal runs where adjacent numeric changes stay within a tolerance."""
from __future__ import annotations

from collections.abc import Iterable


def stable_runs(values: Iterable[float], tolerance: float) -> list[tuple[int, int]]:
    """Return half-open index ranges with bounded adjacent changes."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    data = list(values)
    if not data:
        return []
    runs: list[tuple[int, int]] = []
    start = 0
    for index in range(1, len(data)):
        if abs(data[index] - data[index - 1]) > tolerance:
            runs.append((start, index))
            start = index
    runs.append((start, len(data)))
    return runs


def run_means(values: Iterable[float], tolerance: float) -> list[float]:
    """Compute the mean of every stable run."""
    data = list(values)
    return [sum(data[left:right]) / (right - left) for left, right in stable_runs(data, tolerance)]


if __name__ == "__main__":
    series = [10.0, 10.3, 10.2, 13.5, 13.7, 8.0]
    print(stable_runs(series, 0.5))
    print(run_means(series, 0.5))
