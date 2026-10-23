"""Small LRU cache that exposes operational counters for observability."""
from collections import OrderedDict
from dataclasses import dataclass
from typing import Generic, TypeVar


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0


class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._items: OrderedDict[K, V] = OrderedDict()
        self.stats = CacheStats()

    def get(self, key: K) -> V | None:
        if key not in self._items:
            self.stats.misses += 1
            return None
        self.stats.hits += 1
        self._items.move_to_end(key)
        return self._items[key]

    def put(self, key: K, value: V) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        if len(self._items) > self.capacity:
            self._items.popitem(last=False)
            self.stats.evictions += 1

    def __len__(self) -> int:
        return len(self._items)


if __name__ == "__main__":
    cache = LRUCache[str, int](2)
    cache.put("a", 1)
    cache.put("b", 2)
    print(cache.get("a"), cache.stats)
