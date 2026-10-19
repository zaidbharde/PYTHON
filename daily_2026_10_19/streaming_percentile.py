"""Maintain an exact percentile for a bounded stream of numeric values."""

from __future__ import annotations

import bisect
from collections import deque


class SlidingPercentile:
    def __init__(self, window: int, percentile: float) -> None:
        if window <= 0 or not 0 <= percentile <= 1:
            raise ValueError("window must be positive and percentile must be in [0, 1]")
        self.window = window
        self.percentile = percentile
        self._queue: deque[float] = deque()
        self._sorted: list[float] = []

    def add(self, value: float) -> float:
        bisect.insort(self._sorted, value)
        self._queue.append(value)
        if len(self._queue) > self.window:
            expired = self._queue.popleft()
            self._sorted.pop(bisect.bisect_left(self._sorted, expired))
        rank = self.percentile * (len(self._sorted) - 1)
        lower, upper = int(rank), min(int(rank) + 1, len(self._sorted) - 1)
        fraction = rank - lower
        return self._sorted[lower] * (1 - fraction) + self._sorted[upper] * fraction


if __name__ == "__main__":
    tracker = SlidingPercentile(4, 0.75)
    print([tracker.add(value) for value in [4, 1, 9, 2, 7]])
