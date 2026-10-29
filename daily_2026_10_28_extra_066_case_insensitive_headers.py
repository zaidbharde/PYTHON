"""A small ordered mapping for HTTP headers with case-insensitive names."""
from collections.abc import Iterable, Iterator, MutableMapping


class CaseInsensitiveHeaders(MutableMapping[str, str]):
    """Store header names case-insensitively while retaining their first spelling."""

    _TOKEN = frozenset("!#$%&'*+-.^_`|~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def __init__(self, items: Iterable[tuple[str, str]] = ()) -> None:
        self._data: dict[str, tuple[str, str]] = {}
        for name, value in items:
            self[name] = value

    @staticmethod
    def _validate(name: str, value: str | None = None) -> None:
        if not isinstance(name, str):
            raise TypeError("header name must be a string")
        if not name or any(char not in CaseInsensitiveHeaders._TOKEN for char in name):
            raise ValueError("header name must be a non-empty HTTP token")
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("header value must be a string")
            if any(ord(char) < 32 and char != "\t" or ord(char) == 127 for char in value):
                raise ValueError("header value contains a prohibited control character")

    def __getitem__(self, name: str) -> str:
        self._validate(name)
        return self._data[name.lower()][1]

    def __setitem__(self, name: str, value: str) -> None:
        self._validate(name, value)
        key = name.lower()
        spelling = self._data[key][0] if key in self._data else name
        self._data[key] = (spelling, value)

    def __delitem__(self, name: str) -> None:
        self._validate(name)
        del self._data[name.lower()]

    def __iter__(self) -> Iterator[str]:
        return (spelling for spelling, _ in self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __main_self_check__() -> None:
        headers = CaseInsensitiveHeaders([("Content-Type", "text/plain"), ("X-Count", "1")])
        assert headers["content-TYPE"] == "text/plain"
        headers["CONTENT-type"] = "application/json"
        assert list(headers.items()) == [("Content-Type", "application/json"), ("X-Count", "1")]
        assert len(headers) == 2
        del headers["x-count"]
        assert "X-COUNT" not in headers
        for invalid in ("", "bad name", "Bad:Name"):
            try:
                headers[invalid] = "x"
            except ValueError:
                pass
            else:
                raise AssertionError("invalid header name accepted")
        try:
            headers["X-Test"] = "bad\r\nvalue"
        except ValueError:
            pass
        else:
            raise AssertionError("newline in header value accepted")


if __name__ == "__main__":
    CaseInsensitiveHeaders.__main_self_check__()
