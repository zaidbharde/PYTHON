"""Maintain the largest or smallest K values with bounded memory."""
from __future__ import annotations

import heapq
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def top_k(values: Iterable[T], k: int, *, largest: bool = True) -> list[T]:
    """Return up to K ordered values without sorting the complete input."""
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []
    iterator = iter(values)
    heap: list[T] = []
    for value in iterator:
        candidate = value if largest else _Reverse(value)
        if len(heap) < k:
            heapq.heappush(heap, candidate)
        elif candidate > heap[0]:
            heapq.heapreplace(heap, candidate)
    result = [item if largest else item.value for item in heap]
    return sorted(result, reverse=largest)


class _Reverse:
    def __init__(self, value: T) -> None:
        self.value = value

    def __lt__(self, other: "_Reverse") -> bool:
        return self.value > other.value

    def __gt__(self, other: "_Reverse") -> bool:
        return self.value < other.value


if __name__ == "__main__":
    print(top_k([9, 1, 7, 3, 8], 3))
    print(top_k([9, 1, 7, 3, 8], 2, largest=False))
