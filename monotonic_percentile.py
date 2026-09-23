"""Exact percentile queries over a monotonic stream of numeric values."""
from bisect import bisect_right


class MonotonicPercentiles:
    def __init__(self) -> None:
        self._values: list[float] = []

    def add(self, value: float) -> None:
        if self._values and value < self._values[-1]:
            raise ValueError("values must be added in non-decreasing order")
        self._values.append(float(value))

    def percentile(self, fraction: float) -> float:
        if not self._values:
            raise LookupError("no observations")
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("fraction must be between zero and one")
        position = fraction * (len(self._values) - 1)
        lower = int(position)
        upper = min(lower + 1, len(self._values) - 1)
        weight = position - lower
        return self._values[lower] * (1 - weight) + self._values[upper] * weight

    def rank(self, value: float) -> int:
        return bisect_right(self._values, value)

    def __len__(self) -> int:
        return len(self._values)
