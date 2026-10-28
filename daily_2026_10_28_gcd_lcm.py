"""Compute a least common multiple for any number of integers."""
from math import gcd
from functools import reduce
def lcm(*values: int) -> int:
    """Return non-negative LCM; the empty input has identity 1."""
    return reduce(lambda a, b: 0 if a == 0 or b == 0 else abs(a // gcd(a, b) * b), values, 1)
if __name__ == "__main__":
    assert lcm(6, 8, 9) == 72 and lcm(-4, 6) == 12 and lcm() == 1
    print("LCM checks passed")
