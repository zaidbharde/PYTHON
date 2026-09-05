"""Convert between canonical Roman numerals and integers from 1 through 3999."""

_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_PAIRS = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
          (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
          (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))


def to_roman(number: int) -> str:
    """Return the canonical Roman spelling of a positive integer."""
    if not 1 <= number <= 3999:
        raise ValueError("Roman numerals support integers from 1 to 3999")
    result: list[str] = []
    remaining = number
    for value, symbol in _PAIRS:
        count, remaining = divmod(remaining, value)
        result.append(symbol * count)
    return "".join(result)


def from_roman(numeral: str) -> int:
    """Parse a Roman numeral and reject non-canonical spellings."""
    cleaned = numeral.strip().upper()
    if not cleaned:
        raise ValueError("numeral cannot be empty")
    total = 0
    index = 0
    while index < len(cleaned):
        current = _VALUES.get(cleaned[index])
        if current is None:
            raise ValueError(f"unknown Roman symbol: {cleaned[index]}")
        if index + 1 < len(cleaned) and _VALUES.get(cleaned[index + 1], 0) > current:
            total += _VALUES[cleaned[index + 1]] - current
            index += 2
        else:
            total += current
            index += 1
    if to_roman(total) != cleaned:
        raise ValueError(f"non-canonical Roman numeral: {numeral!r}")
    return total


if __name__ == "__main__":
    for value in (4, 42, 1999):
        numeral = to_roman(value)
        print(f"{value} -> {numeral} -> {from_roman(numeral)}")
