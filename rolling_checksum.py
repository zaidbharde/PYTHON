"""Compute a streaming Adler-style checksum over byte chunks."""
from __future__ import annotations

from collections.abc import Iterable

MODULUS = 65_521


def rolling_checksum(chunks: Iterable[bytes], *, modulus: int = MODULUS) -> int:
    """Return a compact checksum without concatenating the input chunks."""
    if modulus <= 1:
        raise ValueError("modulus must exceed one")
    low, high = 1, 0
    for chunk in chunks:
        for byte in chunk:
            low = (low + byte) % modulus
            high = (high + low) % modulus
    return (high << 16) | low


def checksum_file(path: str, chunk_size: int = 8192) -> int:
    """Checksum a file incrementally, keeping memory bounded."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    with open(path, "rb") as handle:
        return rolling_checksum(iter(lambda: handle.read(chunk_size), b""))


if __name__ == "__main__":
    print(hex(rolling_checksum([b"stream", b"ing"])))
