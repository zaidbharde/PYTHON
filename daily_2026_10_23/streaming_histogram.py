"""Memory-bounded histogram for online numeric measurements."""
from collections import defaultdict
from math import floor
from typing import Iterable


class Histogram:
    def __init__(self, width: float) -> None:
        if width <= 0:
            raise ValueError("bucket width must be positive")
        self.width = width
        self._counts: dict[int, int] = defaultdict(int)
        self.total = 0

    def add(self, value: float) -> None:
        bucket = floor(value / self.width)
        self._counts[bucket] += 1
        self.total += 1

    def extend(self, values: Iterable[float]) -> None:
        for value in values:
            self.add(value)

    def count(self, bucket: int) -> int:
        return self._counts.get(bucket, 0)

    def ranges(self) -> list[tuple[float, float, int]]:
        return [
            (bucket * self.width, (bucket + 1) * self.width, self._counts[bucket])
            for bucket in sorted(self._counts)
        ]

    def density(self) -> dict[int, float]:
        if not self.total:
            return {}
        return {bucket: count / self.total for bucket, count in self._counts.items()}


if __name__ == "__main__":
    histogram = Histogram(10)
    histogram.extend([2, 12, 18, 21])
    print(histogram.ranges())
