"""Interleave iterable inputs one item at a time, skipping exhausted ones."""
from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeVar
T = TypeVar("T")
def round_robin(*sources: Iterable[T]) -> Iterator[T]:
    active = deque(iter(source) for source in sources)
    while active:
        iterator = active.popleft()
        try:
            yield next(iterator)
        except StopIteration:
            continue
        active.append(iterator)
if __name__ == "__main__":
    assert list(round_robin("abc", "XY")) == ["a", "X", "b", "Y", "c"]
    print("round-robin checks passed")
