import time

class TTLCache:
    def __init__(self, ttl_seconds):
        self.ttl = ttl_seconds
        self.store = {}

    def set(self, key, value):
        self.store[key] = (value, time.time())

    def get(self, key):
        if key not in self.store:
            return None
        value, timestamp = self.store[key]
        if time.time() - timestamp > self.ttl:
            del self.store[key]
            return None
        return value


if __name__ == "__main__":
    cache = TTLCache(ttl_seconds=2)
    cache.set("token", "abc123")
    print(cache.get("token"))   # abc123
    time.sleep(2.5)
    print(cache.get("token"))   # None, expired
