"""Validate numeric identifiers and generate their Luhn check digits."""


def _has_ascii_digits(value: str) -> bool:
    return isinstance(value, str) and bool(value) and all("0" <= char <= "9" for char in value)


def _luhn_sum(digits: str) -> int:
    total = 0
    for offset, char in enumerate(reversed(digits)):
        digit = ord(char) - ord("0")
        if offset % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total


def is_valid(identifier: str) -> bool:
    """Return whether an identifier (including its check digit) passes Luhn."""
    return _has_ascii_digits(identifier) and len(identifier) >= 2 and _luhn_sum(identifier) % 10 == 0


def check_digit(payload: str) -> str:
    """Return the single decimal Luhn digit to append to a nonempty payload."""
    if not _has_ascii_digits(payload):
        raise ValueError("payload must be a nonempty string of ASCII digits")
    return str((-_luhn_sum(payload + "0")) % 10)


def append_check_digit(payload: str) -> str:
    """Return payload with its computed Luhn digit appended."""
    return payload + check_digit(payload)


if __name__ == "__main__":
    assert is_valid("79927398713")
    assert append_check_digit("7992739871") == "79927398713"
    assert is_valid(append_check_digit("000123"))
    assert not is_valid("79927398714")
    assert not is_valid("") and not is_valid("１２３") and not is_valid("12-3")
    try:
        check_digit("")
    except ValueError:
        pass
    else:
        raise AssertionError("empty payload should be rejected")
    print("Luhn checksum self-check passed")
