"""Yield fixed-size lists from an iterable, consuming only as needed."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class ChunkedIterator(Iterator[list[T]], Generic[T]):
    """Consume an iterable in batches without reading past each batch."""

    def __init__(self, items: Iterable[T], size: int) -> None:
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("size must be a positive integer")
        self._items = iter(items)
        self._size = size
        self._finished = False

    def __iter__(self) -> ChunkedIterator[T]:
        return self

    def __next__(self) -> list[T]:
        if self._finished:
            raise StopIteration
        batch: list[T] = []
        for _ in range(self._size):
            try:
                batch.append(next(self._items))
            except StopIteration:
                self._finished = True
                break
        if not batch:
            raise StopIteration
        return batch


if __name__ == "__main__":
    assert list(ChunkedIterator(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(ChunkedIterator([], 2)) == []

    class Tracked:
        def __init__(self) -> None:
            self.read = 0

        def __iter__(self) -> Tracked:
            return self

        def __next__(self) -> int:
            value = self.read
            self.read += 1
            return value

    source = Tracked()
    chunks = ChunkedIterator(source, 2)
    assert next(chunks) == [0, 1] and source.read == 2
    assert next(chunks) == [2, 3] and source.read == 4
    try:
        ChunkedIterator([], 0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero size must be rejected")
