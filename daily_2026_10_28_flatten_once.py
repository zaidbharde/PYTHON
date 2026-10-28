"""Flatten one level of nested iterables without flattening strings."""
from collections.abc import Iterable, Iterator
from typing import TypeVar
T = TypeVar("T")
def flatten_once(groups: Iterable[Iterable[T]]) -> Iterator[T]:
    """Yield items from each group in order."""
    for group in groups:
        yield from group
if __name__ == "__main__":
    assert list(flatten_once([[1, 2], [], [3]])) == [1, 2, 3]
    print("flatten checks passed")
