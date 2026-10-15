"""Estimate quantiles from integer histogram buckets."""
from __future__ import annotations

from collections.abc import Iterable


def quantile_from_histogram(buckets: Iterable[tuple[float, int]], q: float) -> float:
    """Return the first bucket boundary reaching the requested rank."""
    if not 0 <= q <= 1:
        raise ValueError("q must be between zero and one")
    normalized = list(buckets)
    if not normalized or any(count < 0 for _, count in normalized):
        raise ValueError("buckets must have non-negative counts")
    total = sum(count for _, count in normalized)
    if total == 0:
        raise ValueError("histogram is empty")
    target = q * (total - 1)
    cumulative = 0
    for edge, count in normalized:
        cumulative += count
        if target < cumulative:
            return edge
    return normalized[-1][0]


def cumulative_points(buckets: Iterable[tuple[float, int]]) -> list[tuple[float, int]]:
    """Convert bucket counts into cumulative counts for plotting."""
    total = 0
    points: list[tuple[float, int]] = []
    for edge, count in buckets:
        if count < 0:
            raise ValueError("count must be non-negative")
        total += count
        points.append((edge, total))
    return points


if __name__ == "__main__":
    print(quantile_from_histogram([(1.0, 2), (2.0, 3), (4.0, 1)], 0.75))
