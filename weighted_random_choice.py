import random
import bisect

class WeightedRandomChoice:
    def __init__(self, items_weights):
        self.items = [item for item, _ in items_weights]
        weights = [w for _, w in items_weights]
        self.cumulative = []
        total = 0
        for w in weights:
            total += w
            self.cumulative.append(total)
        self.total = total

    def pick(self):
        r = random.uniform(0, self.total)
        idx = bisect.bisect_left(self.cumulative, r)
        return self.items[idx]


if __name__ == "__main__":
    items = [("common", 70), ("rare", 25), ("legendary", 5)]
    wrc = WeightedRandomChoice(items)

    counts = {"common": 0, "rare": 0, "legendary": 0}
    for _ in range(10000):
        counts[wrc.pick()] += 1
    print(counts)
