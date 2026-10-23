"""Reproducible weighted choice helpers for experiments and schedulers."""
from random import Random
from typing import Sequence, TypeVar


T = TypeVar("T")


def choose(items: Sequence[T], weights: Sequence[float], seed: int | None = None) -> T:
    if not items or len(items) != len(weights):
        raise ValueError("items and weights must be non-empty and equally sized")
    if any(weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("weights must be non-negative with a positive total")
    generator = Random(seed)
    target = generator.random() * sum(weights)
    cumulative = 0.0
    for item, weight in zip(items, weights):
        cumulative += weight
        if target < cumulative:
            return item
    return items[-1]


def allocate(items: Sequence[T], weights: Sequence[float], draws: int, seed: int = 0) -> list[T]:
    """Draw repeatedly while preserving the same deterministic seed semantics."""
    if draws < 0:
        raise ValueError("draws must be non-negative")
    generator = Random(seed)
    total = sum(weights)
    if not items or len(items) != len(weights) or total <= 0:
        raise ValueError("invalid weighted population")
    result: list[T] = []
    for _ in range(draws):
        result.append(choose(items, weights, generator.randrange(2**63)))
    return result


if __name__ == "__main__":
    print(allocate(["a", "b"], [1, 3], 4))
