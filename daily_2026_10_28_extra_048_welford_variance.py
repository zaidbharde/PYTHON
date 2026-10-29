"""Compute a streaming mean and sample variance with Welford's algorithm."""
import math


class WelfordVariance:
    """Accumulate finite numeric observations in one pass using constant memory."""

    def __init__(self) -> None:
        self.count = 0
        self._mean = 0.0
        self._m2 = 0.0

    def add(self, value: float) -> None:
        """Add one observation; reject non-numeric or non-finite values."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be an int or float")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("value must be finite")
        self.count += 1
        delta = number - self._mean
        self._mean += delta / self.count
        self._m2 += delta * (number - self._mean)

    @property
    def mean(self) -> float:
        """Return the current mean; undefined for an empty accumulator."""
        if not self.count:
            raise ValueError("mean is undefined with no observations")
        return self._mean

    @property
    def sample_variance(self) -> float:
        """Return unbiased sample variance; requires at least two observations."""
        if self.count < 2:
            raise ValueError("sample variance requires at least two observations")
        return self._m2 / (self.count - 1)


if __name__ == "__main__":
    stats = WelfordVariance()
    for item in (2, 4, 4, 4, 5, 5, 7, 9):
        stats.add(item)
    assert stats.count == 8
    assert math.isclose(stats.mean, 5.0)
    assert math.isclose(stats.sample_variance, 32 / 7)
    for property_name in ("mean", "sample_variance"):
        try:
            getattr(WelfordVariance(), property_name)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{property_name} should reject insufficient data")
    for invalid, error in ((float("nan"), ValueError), (True, TypeError), ("1", TypeError)):
        try:
            stats.add(invalid)
        except error:
            pass
        else:
            raise AssertionError(f"{invalid!r} should be rejected")
    print("Welford variance self-check passed")
