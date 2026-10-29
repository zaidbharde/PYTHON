"""Yield values from finite queues in weighted round-robin order."""
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def weighted_queues(queues: Iterable[tuple[Iterable[T], int]]) -> Iterator[T]:
    """Yield each queue's values, granting it ``weight`` turns per round.

    Empty or exhausted queues are removed; weights must be positive integers.
    Queues are consumed lazily, and their relative order is stable each round.
    """
    active: list[tuple[Iterator[T], int]] = []
    for source, weight in queues:
        if isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0:
            raise ValueError("queue weights must be positive integers")
        iterator = iter(source)
        try:
            first = next(iterator)
        except StopIteration:
            continue
        # Store the first value separately through a tiny chained iterator.
        def with_first(value: T, rest: Iterator[T]) -> Iterator[T]:
            yield value
            yield from rest
        active.append((with_first(first, iterator), weight))

    while active:
        survivors: list[tuple[Iterator[T], int]] = []
        for iterator, weight in active:
            for _ in range(weight):
                try:
                    yield next(iterator)
                except StopIteration:
                    break
            else:
                survivors.append((iterator, weight))
        active = survivors


if __name__ == "__main__":
    assert list(weighted_queues([(["a1", "a2", "a3"], 2), (["b1", "b2"], 1)])) == [
        "a1", "a2", "b1", "a3", "b2"
    ]
    assert list(weighted_queues([([], 2), ([1], 1)])) == [1]
    for invalid in (0, -1, True, 1.5):
        try:
            list(weighted_queues([([1], invalid)]))
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid weight: {invalid!r}")
    print("weighted queue checks passed")
