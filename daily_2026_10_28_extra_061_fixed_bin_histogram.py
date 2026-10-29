"""Accumulate observations in a fixed range, tracking values outside it separately."""
from math import isfinite
from numbers import Real


class FixedBinHistogram:
    """Uniform bins over [lower, upper); upper-edge values enter the last bin."""

    def __init__(self, lower: float, upper: float, bins: int) -> None:
        if (not isinstance(lower, Real) or isinstance(lower, bool)
                or not isinstance(upper, Real) or isinstance(upper, bool)
                or not isfinite(lower) or not isfinite(upper) or upper <= lower):
            raise ValueError("bounds must be finite numbers with upper > lower")
        if not isinstance(bins, int) or isinstance(bins, bool) or bins <= 0:
            raise ValueError("bins must be a positive integer")
        self.lower, self.upper, self.bins = float(lower), float(upper), bins
        self.width = (self.upper - self.lower) / bins
        self.counts = [0] * bins
        self.underflow = self.overflow = self.total = 0

    def add(self, value: float) -> int | None:
        """Add a finite real; return its bin index, or None when out of range."""
        if not isinstance(value, Real) or isinstance(value, bool) or not isfinite(value):
            raise ValueError("observation must be a finite real number")
        value = float(value)
        self.total += 1
        if value < self.lower:
            self.underflow += 1
            return None
        if value > self.upper:
            self.overflow += 1
            return None
        index = min(int((value - self.lower) / self.width), self.bins - 1)
        self.counts[index] += 1
        return index

    def extend(self, values: object) -> None:
        """Add each value from an iterable."""
        for value in values:  # type: ignore[union-attr]
            self.add(value)

    def edges(self) -> list[float]:
        """Return the bin boundaries, including both range endpoints."""
        return [self.lower + i * self.width for i in range(self.bins)] + [self.upper]


if __name__ == "__main__":
    histogram = FixedBinHistogram(0, 10, 5)
    assert [histogram.add(x) for x in (-1, 0, 1.9, 2, 9.9, 10, 11)] == [None, 0, 0, 1, 4, 4, None]
    assert histogram.counts == [2, 1, 0, 0, 2]
    assert (histogram.underflow, histogram.overflow, histogram.total) == (1, 1, 7)
    assert histogram.edges() == [0, 2, 4, 6, 8, 10]
    try:
        FixedBinHistogram(1, 1, 3)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid range was accepted")
    print("FixedBinHistogram self-check passed")
