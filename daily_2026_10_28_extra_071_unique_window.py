"""Maintain a bounded, insertion-ordered window of most-recent unique items."""
from collections import deque
from typing import Deque, Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class UniqueWindow(Generic[T]):
    """Keep at most ``capacity`` unique hashable items, newest first by recency."""

    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._items: Deque[T] = deque()
        self._members: set[T] = set()

    def add(self, item: T) -> bool:
        """Refresh ``item`` to newest; return True if it was not already present."""
        hash(item)  # Fail before modifying state when item is not hashable.
        was_new = item not in self._members
        if not was_new:
            self._items.remove(item)
        self._items.append(item)
        self._members.add(item)
        if len(self._items) > self.capacity:
            self._members.remove(self._items.popleft())
        return was_new

    def __contains__(self, item: object) -> bool:
        return item in self._members

    def __len__(self) -> int:
        return len(self._items)

    def most_recent(self) -> tuple[T, ...]:
        """Return a snapshot ordered from most recent to least recent."""
        return tuple(reversed(self._items))


if __name__ == "__main__":
    window = UniqueWindow[int](3)
    assert window.add(1) and window.add(2) and window.add(3)
    assert not window.add(2)
    assert window.most_recent() == (2, 3, 1)
    assert window.add(4) and 1 not in window
    assert len(window) == 3 and window.most_recent() == (4, 2, 3)
    try:
        UniqueWindow(0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero capacity must be rejected")
    print("UniqueWindow self-check passed")
