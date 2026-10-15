"""Build a deterministic weighted choice table using integer tickets."""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class WeightedTable(Generic[T]):
    boundaries: tuple[int, ...]
    values: tuple[T, ...]

    def choose(self, ticket: int) -> T:
        """Choose a value for a ticket in the half-open ticket range."""
        if ticket < 0 or ticket >= self.boundaries[-1]:
            raise ValueError("ticket is outside the table")
        return self.values[bisect_right(self.boundaries, ticket)]


def build_table(entries: Iterable[tuple[T, int]]) -> WeightedTable[T]:
    """Convert positive weights into cumulative ticket boundaries."""
    boundaries: list[int] = []
    values: list[T] = []
    total = 0
    for value, weight in entries:
        if weight <= 0:
            raise ValueError("weights must be positive")
        total += weight
        boundaries.append(total)
        values.append(value)
    if not values:
        raise ValueError("at least one entry is required")
    return WeightedTable(tuple(boundaries), tuple(values))


if __name__ == "__main__":
    table = build_table([("low", 2), ("high", 1)])
    print([table.choose(ticket) for ticket in range(3)])
