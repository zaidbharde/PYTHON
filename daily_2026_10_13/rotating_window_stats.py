"""Maintain exact mean, variance, and extrema for a rotating window."""
from collections import deque
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class WindowStats:
    count: int
    mean: float
    variance: float
    minimum: float | None
    maximum: float | None


class RotatingWindow:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._values: deque[float] = deque()

    def add(self, value: float) -> WindowStats:
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        self._values.append(value)
        if len(self._values) > self.capacity:
            self._values.popleft()
        return self.snapshot()

    def snapshot(self) -> WindowStats:
        values = tuple(self._values)
        if not values:
            return WindowStats(0, 0.0, 0.0, None, None)
        mean = sum(values) / len(values)
        variance = sum((item - mean) ** 2 for item in values) / len(values)
        return WindowStats(len(values), mean, variance, min(values), max(values))


if __name__ == "__main__":
    window = RotatingWindow(3)
    for number in (2, 4, 8, 10):
        print(window.add(number))
