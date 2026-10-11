"""Maintain exact quantiles for a small rolling numeric window."""
from bisect import bisect_left, insort
from collections import deque


class RollingQuantiles:
    def __init__(self, size: int):
        if size < 1:
            raise ValueError("window size must be positive")
        self.size = size
        self._queue = deque()
        self._sorted: list[float] = []

    def add(self, value: float) -> None:
        """Add a value and evict the oldest value when the window is full."""
        insort(self._sorted, value)
        self._queue.append(value)
        if len(self._queue) > self.size:
            expired = self._queue.popleft()
            self._sorted.pop(bisect_left(self._sorted, expired))

    def quantile(self, fraction: float) -> float:
        """Return a linearly interpolated quantile in the current window."""
        if not self._sorted:
            raise ValueError("cannot query an empty window")
        if not 0 <= fraction <= 1:
            raise ValueError("fraction must be between zero and one")
        position = fraction * (len(self._sorted) - 1)
        lower = int(position)
        upper = min(lower + 1, len(self._sorted) - 1)
        blend = position - lower
        return self._sorted[lower] * (1 - blend) + self._sorted[upper] * blend

    def summary(self) -> dict[str, float]:
        """Return common quantiles useful for latency and sensor dashboards."""
        if not self._sorted:
            return {}
        return {name: self.quantile(level) for name, level in
                (("p50", 0.50), ("p90", 0.90), ("p99", 0.99))}

    def __len__(self) -> int:
        return len(self._queue)


if __name__ == "__main__":
    window = RollingQuantiles(4)
    for reading in (12, 8, 20, 15, 11):
        window.add(reading)
    print(window.summary())
