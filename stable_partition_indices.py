"""Partition records while preserving the relative order of each group."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def stable_partition(values: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """Return matching and non-matching values in their original order."""
    matching: list[T] = []
    remaining: list[T] = []
    for value in values:
        (matching if predicate(value) else remaining).append(value)
    return matching, remaining


def partition_indices(values: Iterable[T], predicate: Callable[[T], bool]) -> list[int]:
    """Return the original indices with matches first, stably ordered."""
    data = list(values)
    yes, no = stable_partition(enumerate(data), lambda pair: predicate(pair[1]))
    return [index for index, _ in yes + no]


def compact_sorted(values: Iterable[int]) -> list[int]:
    """Move zeroes to the end without changing the order of non-zero values."""
    nonzero, zero = stable_partition(values, lambda value: value != 0)
    return nonzero + zero


if __name__ == "__main__":
    print(compact_sorted([0, 4, 0, 2, 7]))
