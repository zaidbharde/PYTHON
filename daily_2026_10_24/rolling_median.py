"""Maintain a rolling median with two heaps and lazy deletion."""
from __future__ import annotations

import heapq
from collections import Counter, deque


class RollingMedian:
    """Compute exact medians for a fixed-size stream window."""

    def __init__(self, width: int) -> None:
        if width <= 0:
            raise ValueError("window width must be positive")
        self.width = width
        self.values: deque[float] = deque()
        self.lower: list[float] = []
        self.upper: list[float] = []
        self.delayed: Counter[float] = Counter()

    def add(self, value: float) -> float:
        """Insert a value, evicting the oldest value when necessary."""
        self.values.append(value)
        if not self.lower or value <= -self.lower[0]:
            heapq.heappush(self.lower, -value)
        else:
            heapq.heappush(self.upper, value)
        if len(self.values) > self.width:
            self._remove(self.values.popleft())
        self._rebalance()
        return self.median

    @property
    def median(self) -> float:
        """Return the current median, or fail for an empty stream."""
        if not self.values:
            raise ValueError("median is undefined for an empty stream")
        self._prune(self.lower)
        self._prune(self.upper)
        if len(self.lower) > len(self.upper):
            return -self.lower[0]
        return (-self.lower[0] + self.upper[0]) / 2

    def _remove(self, value: float) -> None:
        self.delayed[value] += 1
        if value <= -self.lower[0]:
            self._prune(self.lower)
        else:
            self._prune(self.upper)

    def _rebalance(self) -> None:
        self._prune(self.lower)
        self._prune(self.upper)
        while len(self.lower) > len(self.upper) + 1:
            heapq.heappush(self.upper, -heapq.heappop(self.lower))
        while len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))

    def _prune(self, heap: list[float]) -> None:
        while heap:
            value = -heap[0] if heap is self.lower else heap[0]
            if not self.delayed[value]:
                return
            self.delayed[value] -= 1
            heapq.heappop(heap)


if __name__ == "__main__":
    stream = RollingMedian(3)
    assert stream.add(5) == 5
    assert stream.add(1) == 3
    assert stream.add(9) == 5
    assert stream.add(2) == 2
    print("rolling median checks passed")
