"""Encode and decode nonnegative integers using bases 2 through 36."""


class BaseNCodec:
    """Stateless base converter using 0-9 and A-Z as its digit alphabet."""

    ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @staticmethod
    def _check_base(base: int) -> None:
        if isinstance(base, bool) or not isinstance(base, int) or not 2 <= base <= 36:
            raise ValueError("base must be an integer from 2 through 36")

    @classmethod
    def encode(cls, value: int, base: int) -> str:
        """Return the uppercase representation of a nonnegative integer."""
        cls._check_base(base)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("value must be a nonnegative integer")
        if value == 0:
            return "0"
        digits: list[str] = []
        while value:
            value, remainder = divmod(value, base)
            digits.append(cls.ALPHABET[remainder])
        return "".join(reversed(digits))

    @classmethod
    def decode(cls, text: str, base: int) -> int:
        """Parse a digit string (case-insensitive) in the selected base."""
        cls._check_base(base)
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a nonempty string")
        value = 0
        for char in text.upper():
            digit = cls.ALPHABET.find(char)
            if digit < 0 or digit >= base:
                raise ValueError(f"invalid digit {char!r} for base {base}")
            value = value * base + digit
        return value


if __name__ == "__main__":
    for number in (0, 1, 35, 255, 123456789, 10**40):
        for radix in (2, 8, 10, 16, 36):
            assert BaseNCodec.decode(BaseNCodec.encode(number, radix), radix) == number
    assert BaseNCodec.encode(255, 16) == "FF"
    assert BaseNCodec.decode("ff", 16) == 255
    for bad_value, bad_base in ((-1, 2), (1, 1), (1, 37), (True, 2)):
        try:
            BaseNCodec.encode(bad_value, bad_base)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input was accepted")
    print("BaseNCodec self-check passed")
