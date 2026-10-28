"""Fixed-capacity FIFO queue backed by a circular buffer."""
from typing import Generic, TypeVar
T = TypeVar("T")
class CircularQueue(Generic[T]):
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._items: list[T | None] = [None] * capacity
        self._head = self._size = 0
    def __len__(self) -> int:
        return self._size
    def push(self, item: T) -> None:
        if self._size == len(self._items):
            raise OverflowError("queue is full")
        tail = (self._head + self._size) % len(self._items)
        self._items[tail] = item
        self._size += 1
    def pop(self) -> T:
        if not self._size:
            raise IndexError("pop from empty queue")
        item = self._items[self._head]
        self._items[self._head] = None
        self._head = (self._head + 1) % len(self._items)
        self._size -= 1
        return item  # type: ignore[return-value]
if __name__ == "__main__":
    queue: CircularQueue[int] = CircularQueue(2)
    queue.push(1); queue.push(2); assert queue.pop() == 1
    queue.push(3); assert [queue.pop(), queue.pop()] == [2, 3]
