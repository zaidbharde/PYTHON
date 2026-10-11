"""A bounded priority queue with stable FIFO ordering within each priority."""
from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from typing import Any


@dataclass(order=True)
class _Entry:
    priority: int
    sequence: int
    value: Any = field(compare=False)


class PriorityFairQueue:
    def __init__(self, capacity: int | None = None):
        if capacity is not None and capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._items: list[_Entry] = []
        self._sequence = count()

    def put(self, value: Any, priority: int = 0) -> None:
        """Insert an item, rejecting new work when capacity is exhausted."""
        if self.capacity is not None and len(self._items) >= self.capacity:
            raise OverflowError("queue capacity reached")
        heappush(self._items, _Entry(priority, next(self._sequence), value))

    def get(self) -> Any:
        """Remove the highest-priority item, where lower numbers win."""
        if not self._items:
            raise IndexError("get from empty queue")
        return heappop(self._items).value

    def peek(self) -> Any:
        """Inspect the next item without removing it."""
        if not self._items:
            raise IndexError("peek from empty queue")
        return self._items[0].value

    def drain(self) -> list[Any]:
        """Return all queued values in service order."""
        return [self.get() for _ in range(len(self._items))]

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)


if __name__ == "__main__":
    queue = PriorityFairQueue(3)
    queue.put("background", priority=5)
    queue.put("urgent", priority=1)
    queue.put("normal", priority=3)
    print(queue.drain())
