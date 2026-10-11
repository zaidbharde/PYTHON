"""Iterative segment tree supporting range sums and point updates."""


class SegmentTree:
    def __init__(self, values: list[int | float]):
        if not values:
            raise ValueError("segment tree requires at least one value")
        self._size = 1
        while self._size < len(values):
            self._size *= 2
        self._tree = [0] * (2 * self._size)
        for index, value in enumerate(values):
            self._tree[self._size + index] = value
        for index in range(self._size - 1, 0, -1):
            self._tree[index] = self._tree[index * 2] + self._tree[index * 2 + 1]

    def update(self, index: int, value: int | float) -> None:
        """Replace one source value and refresh its ancestors."""
        if not 0 <= index < self._size:
            raise IndexError("index outside source range")
        position = self._size + index
        self._tree[position] = value
        position //= 2
        while position:
            self._tree[position] = self._tree[position * 2] + self._tree[position * 2 + 1]
            position //= 2

    def query(self, left: int, right: int) -> int | float:
        """Return the half-open range sum [left, right)."""
        if not 0 <= left <= right <= self._size:
            raise ValueError("invalid half-open range")
        left += self._size
        right += self._size
        total = 0
        while left < right:
            if left & 1:
                total += self._tree[left]
                left += 1
            if right & 1:
                right -= 1
                total += self._tree[right]
            left //= 2
            right //= 2
        return total


if __name__ == "__main__":
    tree = SegmentTree([4, 2, 7, 1, 3])
    tree.update(2, 9)
    print(tree.query(1, 4))
