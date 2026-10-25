"""Maintain an exact percentile while values arrive one at a time."""
from heapq import heappop, heappush


class StreamingPercentile:
    def __init__(self, percentile: float = 0.5) -> None:
        if not 0.0 <= percentile <= 1.0:
            raise ValueError("percentile must be between zero and one")
        self.percentile = percentile
        self._lower: list[int] = []
        self._upper: list[int] = []

    def add(self, value: int) -> None:
        if not self._lower or value <= -self._lower[0]:
            heappush(self._lower, -value)
        else:
            heappush(self._upper, value)
        self._rebalance()

    def _rebalance(self) -> None:
        target = int((len(self._lower) + len(self._upper)) * self.percentile)
        while len(self._lower) > max(1, target + 1):
            heappush(self._upper, -heappop(self._lower))
        while len(self._lower) < max(1, target):
            heappush(self._lower, -heappop(self._upper))

    def value(self) -> float:
        if not self._lower and not self._upper:
            raise ValueError("percentile is undefined for an empty stream")
        if self.percentile == 1.0:
            return float(self._upper[0] if self._upper else -self._lower[0])
        return float(-self._lower[0])


if __name__ == "__main__":
    tracker = StreamingPercentile(0.5)
    for sample in [8, 2, 9, 4, 7]:
        tracker.add(sample)
    print(f"median={tracker.value():.0f}")
