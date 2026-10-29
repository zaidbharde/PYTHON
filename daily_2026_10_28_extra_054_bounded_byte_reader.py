"""Read a binary stream in capped chunks without exceeding a byte budget."""
from collections.abc import Iterator
from typing import BinaryIO


class BoundedByteReader(Iterator[bytes]):
    """Iterate over at most ``max_bytes`` from a stream in chunks up to ``chunk_size``."""

    def __init__(self, stream: BinaryIO, max_bytes: int, chunk_size: int = 64 * 1024) -> None:
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
            raise ValueError("max_bytes must be a non-negative integer")
        if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if not callable(getattr(stream, "read", None)):
            raise TypeError("stream must provide a read(size) method")
        self._stream = stream
        self._remaining = max_bytes
        self.chunk_size = chunk_size
        self.bytes_read = 0

    def __iter__(self) -> "BoundedByteReader":
        return self

    def __next__(self) -> bytes:
        if self._remaining == 0:
            raise StopIteration
        chunk = self._stream.read(min(self.chunk_size, self._remaining))
        if not isinstance(chunk, bytes):
            raise TypeError("binary stream read() must return bytes")
        if not chunk:
            self._remaining = 0
            raise StopIteration
        if len(chunk) > min(self.chunk_size, self._remaining):
            raise OSError("stream returned more bytes than requested")
        self._remaining -= len(chunk)
        self.bytes_read += len(chunk)
        return chunk


if __name__ == "__main__":
    from io import BytesIO

    reader = BoundedByteReader(BytesIO(b"abcdefghij"), max_bytes=7, chunk_size=3)
    chunks = list(reader)
    assert chunks == [b"abc", b"def", b"g"]
    assert reader.bytes_read == 7
    assert list(BoundedByteReader(BytesIO(b"abc"), 0)) == []
    for args in ((BytesIO(), -1), (BytesIO(), 1, 0), (BytesIO(), True)):
        try:
            BoundedByteReader(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid arguments accepted: {args}")
    print("BoundedByteReader self-check passed")
