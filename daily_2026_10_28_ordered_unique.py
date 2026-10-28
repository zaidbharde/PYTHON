"""Remove duplicates while preserving first-seen order."""
from collections.abc import Iterable, Hashable
from typing import TypeVar
T = TypeVar("T", bound=Hashable)
def ordered_unique(items: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    result: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
if __name__ == "__main__":
    assert ordered_unique(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
    print("ordered unique checks passed")
