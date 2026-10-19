"""Merge appointments and return the gaps available for booking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Slot:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("slot end cannot precede its start")


def free_slots(appointments: list[Slot], day_start: int, day_end: int) -> list[Slot]:
    if day_end < day_start:
        raise ValueError("invalid day bounds")
    merged: list[Slot] = []
    for slot in sorted(appointments):
        if not merged or slot.start > merged[-1].end:
            merged.append(slot)
        else:
            previous = merged[-1]
            merged[-1] = Slot(previous.start, max(previous.end, slot.end))
    gaps: list[Slot] = []
    cursor = day_start
    for slot in merged:
        clipped = Slot(max(slot.start, day_start), min(slot.end, day_end))
        if clipped.start > cursor:
            gaps.append(Slot(cursor, clipped.start))
        cursor = max(cursor, clipped.end)
    if cursor < day_end:
        gaps.append(Slot(cursor, day_end))
    return [gap for gap in gaps if gap.start < gap.end]


if __name__ == "__main__":
    print(free_slots([Slot(9, 11), Slot(10, 13), Slot(15, 16)], 8, 18))
