"""Encode and decode unsigned integers using canonical LEB128 varints."""


def encode(value: int) -> bytes:
    """Return the minimal unsigned LEB128 representation of *value*."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("value must be an integer")
    if value < 0:
        raise ValueError("value must be non-negative")
    encoded = bytearray()
    while value >= 0x80:
        encoded.append((value & 0x7F) | 0x80)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def decode(data: bytes | bytearray | memoryview) -> tuple[int, int]:
    """Decode one varint; return ``(value, bytes_consumed)``.

    Raises ValueError for an empty, truncated, or non-canonical encoding.
    Extra bytes are left for the caller to decode as subsequent values.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like")
    value = shift = 0
    for index, byte in enumerate(data):
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            consumed = index + 1
            if consumed > 1 and byte == 0:
                raise ValueError("non-canonical varint")
            return value, consumed
        shift += 7
    if not data:
        raise ValueError("varint data is empty")
    raise ValueError("truncated varint")


if __name__ == "__main__":
    samples = [0, 1, 127, 128, 300, 2**64 - 1, 2**100]
    for number in samples:
        encoded = encode(number)
        assert decode(encoded) == (number, len(encoded))
    assert decode(encode(5) + encode(300)) == (5, 1)
    for invalid in (b"", b"\x80", b"\x80\x00"):
        try:
            decode(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid encoding accepted: {invalid!r}")
    for invalid in (-1, True, 1.5):
        try:
            encode(invalid)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid value accepted: {invalid!r}")
