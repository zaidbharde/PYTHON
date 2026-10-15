"""Deduplicate ordered events while retaining the latest payload for each key."""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")

@dataclass(frozen=True)
class Event:
    key: str
    sequence: int
    payload: object


def latest_by_key(events: Iterable[tuple[K, T]]) -> list[tuple[K, T]]:
    """Keep one value per key, in the order keys were first observed."""
    latest: OrderedDict[K, T] = OrderedDict()
    for key, value in events:
        latest[key] = value
    return list(latest.items())


def compact_events(events: Iterable[Event]) -> list[Event]:
    """Keep the highest-sequence event for each key and sort by sequence."""
    selected: dict[str, Event] = {}
    for event in events:
        previous = selected.get(event.key)
        if previous is None or event.sequence > previous.sequence:
            selected[event.key] = event
    return sorted(selected.values(), key=lambda event: event.sequence)


if __name__ == "__main__":
    sample = [Event("a", 1, "old"), Event("a", 3, "new"), Event("b", 2, "only")]
    print(compact_events(sample))
