"""Build comparable keys that order mixed text-and-number labels naturally."""
from __future__ import annotations

import re
from typing import TypeAlias

Token: TypeAlias = tuple[int, int, str]
NaturalKey: TypeAlias = tuple[Token, ...]
_DIGITS = re.compile(r"([0-9]+)")


class NaturalSortKey:
    """Callable key factory for case-insensitive natural sorting of strings.

    Numeric runs compare by integer value; equal values prefer fewer leading
    zeroes. Text compares case-insensitively; equal keys retain input order.
    """

    def __call__(self, value: str) -> NaturalKey:
        if not isinstance(value, str):
            raise TypeError("NaturalSortKey expects a string")
        tokens: list[Token] = []
        for part in _DIGITS.split(value):
            if not part:
                continue
            if part.isascii() and part.isdigit():
                significant = part.lstrip("0") or "0"
                zero_count = len(part) - len(significant)
                # Length then digits compares arbitrary-size numbers without int limits.
                tokens.append((0, len(significant), significant + "\0" + str(zero_count)))
            else:
                tokens.append((1, 0, part.casefold()))
        return tuple(tokens)


def natural_sorted(values: list[str]) -> list[str]:
    """Return a new list ordered by :class:`NaturalSortKey`."""
    if not isinstance(values, list):
        raise TypeError("values must be a list of strings")
    key = NaturalSortKey()
    return sorted(values, key=key)


if __name__ == "__main__":
    labels = ["item10", "item2", "Item1", "item02", "item"]
    assert natural_sorted(labels) == ["item", "Item1", "item2", "item02", "item10"]
    assert natural_sorted([]) == []
    assert NaturalSortKey()("part0003") < NaturalSortKey()("part12")
    try:
        NaturalSortKey()(3)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string input must be rejected")
    print("NaturalSortKey self-check passed")
