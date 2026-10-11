"""Manage busy time ranges and answer availability queries."""
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class TimeRange:
    start: int
    end: int

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("range end must be greater than start")


class IntervalCalendar:
    def __init__(self, ranges: list[TimeRange] | None = None):
        self._ranges: list[TimeRange] = []
        for item in ranges or []:
            self.book(item)

    def book(self, item: TimeRange) -> None:
        """Add a range unless it overlaps an existing booking."""
        for current in self._ranges:
            if item.start < current.end and current.start < item.end:
                raise ValueError("booking overlaps an existing range")
        self._ranges.append(item)
        self._ranges.sort()

    def available(self, start: int, end: int) -> bool:
        """Return whether an entire half-open range is free."""
        if end <= start:
            raise ValueError("end must be greater than start")
        return all(end <= item.start or start >= item.end for item in self._ranges)

    def gaps(self, start: int, end: int) -> list[TimeRange]:
        """Return free gaps inside the requested horizon."""
        if end <= start:
            raise ValueError("end must be greater than start")
        cursor = start
        free: list[TimeRange] = []
        for item in self._ranges:
            if item.end <= start:
                continue
            if item.start >= end:
                break
            if cursor < item.start:
                free.append(TimeRange(cursor, min(item.start, end)))
            cursor = max(cursor, item.end)
        if cursor < end:
            free.append(TimeRange(cursor, end))
        return free

    def __len__(self) -> int:
        return len(self._ranges)


if __name__ == "__main__":
    calendar = IntervalCalendar([TimeRange(2, 4), TimeRange(7, 9)])
    print(calendar.gaps(0, 10))
