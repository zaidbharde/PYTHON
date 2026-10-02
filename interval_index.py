"""Small interval index supporting overlap insertion and point queries."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Interval:
    start: int
    end: int
    label: str

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("interval start must not exceed end")

    def contains(self, point: int) -> bool:
        return self.start <= point <= self.end


class IntervalIndex:
    def __init__(self) -> None:
        self._items: list[Interval] = []

    def add(self, start: int, end: int, label: str) -> None:
        item = Interval(start, end, label)
        self._items.append(item)
        self._items.sort(key=lambda interval: (interval.start, interval.end))

    def at(self, point: int) -> list[str]:
        matches: list[str] = []
        for item in self._items:
            if item.start > point:
                break
            if item.contains(point):
                matches.append(item.label)
        return matches

    def overlaps(self, start: int, end: int) -> list[Interval]:
        if start > end:
            raise ValueError("query start must not exceed end")
        return [
            item
            for item in self._items
            if item.start <= end and item.end >= start
        ]

    def __len__(self) -> int:
        return len(self._items)


if __name__ == "__main__":
    index = IntervalIndex()
    index.add(10, 20, "maintenance")
    index.add(15, 17, "deploy")
    print(index.at(16))
