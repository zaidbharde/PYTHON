"""Split an iterable into matching and non-matching items."""
from collections.abc import Callable, Iterable
from typing import TypeVar
T = TypeVar("T")
def partition_by(items: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    yes: list[T] = []
    no: list[T] = []
    for item in items:
        (yes if predicate(item) else no).append(item)
    return yes, no
if __name__ == "__main__":
    assert partition_by(range(6), lambda n: n % 2 == 0) == ([0, 2, 4], [1, 3, 5])
    print("partition checks passed")
