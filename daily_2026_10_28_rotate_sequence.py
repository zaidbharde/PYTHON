"""Rotate a sequence left or right without mutating the input."""
from collections.abc import Sequence
from typing import TypeVar
T = TypeVar("T")
def rotate(items: Sequence[T], steps: int) -> list[T]:
    """Positive steps rotate left; negative steps rotate right."""
    values = list(items)
    if not values:
        return values
    offset = steps % len(values)
    return values[offset:] + values[:offset]
if __name__ == "__main__":
    assert rotate([1, 2, 3, 4], 1) == [2, 3, 4, 1]
    assert rotate([1, 2, 3], -1) == [3, 1, 2]
    print("rotation checks passed")
