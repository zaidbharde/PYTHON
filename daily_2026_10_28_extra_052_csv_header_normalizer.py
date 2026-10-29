"""Deterministically make CSV column headers unique without changing first occurrences."""

from collections.abc import Iterable


class CsvHeaderNormalizer:
    """Normalize repeated header strings by appending stable numeric suffixes."""

    @staticmethod
    def normalize(headers: Iterable[str]) -> list[str]:
        """Return unique headers; duplicates become ``name_2``, ``name_3``, etc.

        Suffixes avoid both previously emitted names and names already present
        later in the input, so an original ``name_2`` is never overwritten.
        Matching is case-sensitive and whitespace is preserved.
        """
        if isinstance(headers, (str, bytes)):
            raise TypeError("headers must be an iterable of strings, not a string")
        try:
            items = list(headers)
        except TypeError as exc:
            raise TypeError("headers must be an iterable of strings") from exc
        if any(not isinstance(header, str) for header in items):
            raise TypeError("every header must be a string")

        reserved = set(items)
        seen: set[str] = set()
        result: list[str] = []
        next_suffix: dict[str, int] = {}
        for header in items:
            if header not in seen:
                name = header
            else:
                suffix = next_suffix.get(header, 2)
                name = f"{header}_{suffix}"
                while name in seen or name in reserved:
                    suffix += 1
                    name = f"{header}_{suffix}"
                next_suffix[header] = suffix + 1
            seen.add(name)
            result.append(name)
        return result


if __name__ == "__main__":
    assert CsvHeaderNormalizer.normalize(["id", "name", "id", "id"]) == [
        "id", "name", "id_2", "id_3"
    ]
    assert CsvHeaderNormalizer.normalize(["x", "x", "x_2", "x"]) == [
        "x", "x_3", "x_2", "x_4"
    ]
    assert CsvHeaderNormalizer.normalize(["", "", "A", "a"]) == [
        "", "_2", "A", "a"
    ]
    try:
        CsvHeaderNormalizer.normalize(["ok", None])  # type: ignore[list-item]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string header should be rejected")
    print("CsvHeaderNormalizer self-check passed")
