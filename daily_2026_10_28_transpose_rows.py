"""Transpose equally sized rows, with a clear ragged-input error."""
from collections.abc import Sequence
from typing import TypeVar
T = TypeVar("T")
def transpose(rows: Sequence[Sequence[T]]) -> list[list[T]]:
    if not rows:
        return []
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("rows must have equal lengths")
    return [list(column) for column in zip(*rows)]
if __name__ == "__main__":
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
    assert transpose([[], []]) == []
    print("transpose checks passed")
