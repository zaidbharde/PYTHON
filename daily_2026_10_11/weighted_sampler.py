"""Deterministic weighted sampling helpers using an injected random source."""
from bisect import bisect
from random import Random
from typing import Sequence, TypeVar


T = TypeVar("T")


def choose(items: Sequence[T], weights: Sequence[float], rng: Random | None = None) -> T:
    """Choose one item proportional to its non-negative weight."""
    if not items or len(items) != len(weights):
        raise ValueError("items and weights must be equally sized and non-empty")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights cannot be negative")
    total = sum(weights)
    if total <= 0:
        raise ValueError("at least one weight must be positive")
    generator = rng or Random()
    threshold = generator.random() * total
    cumulative = []
    running = 0.0
    for weight in weights:
        running += weight
        cumulative.append(running)
    return items[bisect(cumulative, threshold)]


def allocate_counts(weights: Sequence[float], count: int) -> list[int]:
    """Allocate integer slots by largest remainder, preserving total count."""
    if count < 0 or not weights or any(weight < 0 for weight in weights):
        raise ValueError("count and weights must be non-negative and non-empty")
    total = sum(weights)
    if total == 0:
        raise ValueError("at least one weight must be positive")
    quotas = [weight * count / total for weight in weights]
    result = [int(quota) for quota in quotas]
    remaining = count - sum(result)
    order = sorted(range(len(weights)), key=lambda i: quotas[i] - result[i], reverse=True)
    for index in order[:remaining]:
        result[index] += 1
    return result


if __name__ == "__main__":
    print(allocate_counts([1, 2, 1], 7))
