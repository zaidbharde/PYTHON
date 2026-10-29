"""Compact non-negative integer set backed by a Python integer."""


class BitSet:
    """Set with O(1) membership and bitwise set operations."""
    def __init__(self, values=()) -> None:
        self._bits = 0
        try:
            for value in values: self.add(value)
        except TypeError as exc:
            raise TypeError("values must be an iterable of non-negative integers") from exc

    @staticmethod
    def _check(value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("elements must be integers (not booleans)")
        if value < 0: raise ValueError("elements must be non-negative")

    def add(self, value: int) -> None:
        self._check(value); self._bits |= 1 << value

    def discard(self, value: int) -> None:
        self._check(value); self._bits &= ~(1 << value)

    def __contains__(self, value: object) -> bool:
        return (isinstance(value, int) and not isinstance(value, bool)
                and value >= 0 and bool(self._bits & (1 << value)))

    def __len__(self) -> int: return self._bits.bit_count()

    def __iter__(self):
        bits = self._bits
        while bits:
            low = bits & -bits; yield low.bit_length() - 1; bits ^= low

    def _combine(self, other: "BitSet", op: str) -> "BitSet":
        if not isinstance(other, BitSet): raise TypeError("expected another BitSet")
        result = BitSet()
        result._bits = {"union": self._bits | other._bits,
                        "intersection": self._bits & other._bits,
                        "difference": self._bits & ~other._bits}[op]
        return result

    def union(self, other: "BitSet") -> "BitSet": return self._combine(other, "union")
    def intersection(self, other: "BitSet") -> "BitSet": return self._combine(other, "intersection")
    def difference(self, other: "BitSet") -> "BitSet": return self._combine(other, "difference")


if __name__ == "__main__":
    a, b = BitSet([0, 3, 8]), BitSet([3, 5])
    assert list(a) == [0, 3, 8] and len(a) == 3 and 8 in a and 2 not in a
    assert list(a.union(b)) == [0, 3, 5, 8]
    assert list(a.intersection(b)) == [3] and list(a.difference(b)) == [0, 8]
    a.discard(3); assert 3 not in a
    for bad in (-1, True, 1.5):
        try: a.add(bad)
        except (TypeError, ValueError): pass
        else: raise AssertionError(f"accepted invalid element: {bad!r}")
    print("BitSet self-check passed")
