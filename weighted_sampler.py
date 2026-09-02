"""Deterministic-friendly weighted sampling helpers using a caller-provided RNG."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar


T = TypeVar("T")


def choose_one(items: Sequence[T], weights: Sequence[float], rng: random.Random) -> T:
    """Choose one item according to non-negative relative weights."""
    if len(items) != len(weights) or not items:
        raise ValueError("items and weights must have the same non-zero length")
    if any(weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("weights must be non-negative and have a positive sum")
    return rng.choices(items, weights=weights, k=1)[0]


def sample(items: Sequence[T], weights: Sequence[float], count: int, rng: random.Random) -> list[T]:
    """Draw distinct items by repeatedly removing the selected weight."""
    if count < 0 or count > len(items):
        raise ValueError("count must be between zero and the number of items")
    if len(items) != len(weights):
        raise ValueError("items and weights must have the same length")
    remaining_items = list(items)
    remaining_weights = list(weights)
    result: list[T] = []
    for _ in range(count):
        selected = choose_one(remaining_items, remaining_weights, rng)
        index = remaining_items.index(selected)
        result.append(remaining_items.pop(index))
        remaining_weights.pop(index)
    return result


if __name__ == "__main__":
    generator = random.Random(7)
    print(sample(["low", "medium", "high"], [1, 3, 6], 2, generator))
