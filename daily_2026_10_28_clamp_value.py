"""Clamp numeric values to inclusive bounds."""
from typing import TypeVar
N = TypeVar("N", int, float)
def clamp(value: N, lower: N, upper: N) -> N:
    """Return value constrained to [lower, upper]."""
    if lower > upper:
        raise ValueError("lower bound exceeds upper bound")
    return min(max(value, lower), upper)
if __name__ == "__main__":
    assert clamp(5, 0, 3) == 3 and clamp(-1.0, 0.0, 4.0) == 0.0
    print("clamp checks passed")
