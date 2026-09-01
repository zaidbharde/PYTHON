"""Score numeric observations for outliers using a robust MAD-based detector."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class ScoredValue:
    value: float
    score: float
    anomalous: bool


def score_values(values: Iterable[float], threshold: float = 3.5) -> list[ScoredValue]:
    data = [float(value) for value in values]
    if not data:
        return []
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    center = median(data)
    deviations = [abs(value - center) for value in data]
    mad = median(deviations)
    if mad == 0:
        return [ScoredValue(value, 0.0, value != center) for value in data]
    scale = 0.6745 / mad
    return [
        ScoredValue(value, abs(value - center) * scale,
                    abs(value - center) * scale > threshold)
        for value in data
    ]


def anomalies(values: Iterable[float], threshold: float = 3.5) -> list[float]:
    return [item.value for item in score_values(values, threshold) if item.anomalous]


if __name__ == "__main__":
    readings = [10.1, 10.0, 9.9, 10.2, 42.0]
    print(anomalies(readings))
