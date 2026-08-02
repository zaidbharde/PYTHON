from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


if __name__ == "__main__":
    lru = LRUCache(2)
    lru.put(1, "a")
    lru.put(2, "b")
    print(lru.get(1))    # a
    lru.put(3, "c")       # evicts key 2
    print(lru.get(2))    # -1
    print(lru.get(3))    # c
