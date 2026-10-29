"""Replace selected half-open character spans without shifting later offsets."""

from collections.abc import Iterable


def redact_spans(
    text: str,
    spans: Iterable[tuple[int, int]],
    replacement: str = "[REDACTED]",
) -> str:
    """Replace ``[start, end)`` spans, interpreted against the original text.

    Spans may be supplied in any order; overlaps are rejected. Empty spans are
    valid no-ops. Applying right to left keeps all original offsets stable.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(replacement, str):
        raise TypeError("replacement must be a string")

    checked: list[tuple[int, int]] = []
    for span in spans:
        if not isinstance(span, (tuple, list)) or len(span) != 2:
            raise TypeError("each span must contain exactly two integer offsets")
        start, end = span
        if (not isinstance(start, int) or isinstance(start, bool)
                or not isinstance(end, int) or isinstance(end, bool)):
            raise TypeError("span offsets must be integers")
        if start < 0 or end < start or end > len(text):
            raise ValueError(f"invalid span ({start}, {end}) for text of length {len(text)}")
        checked.append((start, end))

    checked.sort()
    for previous, current in zip(checked, checked[1:]):
        if current[0] < previous[1]:
            raise ValueError(f"overlapping spans: {previous} and {current}")

    result = text
    for start, end in reversed(checked):
        if start == end:
            continue
        result = result[:start] + replacement + result[end:]
    return result


if __name__ == "__main__":
    original = "Account 1234; code 5678"
    assert redact_spans(original, [(19, 23), (8, 12)]) == "Account [REDACTED]; code [REDACTED]"
    assert redact_spans("abc", [(1, 1)]) == "abc"
    assert redact_spans("abcdef", [(1, 3), (3, 5)], "*") == "a**f"
    for invalid in ([(2, 4), (3, 5)], [(-1, 1)], [(0, 4)]):
        try:
            redact_spans("abc", invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected invalid spans to fail: {invalid}")
