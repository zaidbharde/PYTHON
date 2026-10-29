"""Normalize CRLF and CR line endings while preserving all other text."""


def normalize_newlines(text: str) -> str:
    """Return *text* with CRLF and lone CR endings converted to LF.

    Non-string inputs are rejected rather than coerced, and every character
    other than carriage returns participating in a line ending is preserved.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return text.replace("\r\n", "\n").replace("\r", "\n")


if __name__ == "__main__":
    assert normalize_newlines("") == ""
    assert normalize_newlines("one\r\ntwo\rthree\nfour") == "one\ntwo\nthree\nfour"
    assert normalize_newlines("\r\r\n\n") == "\n\n\n"
    assert normalize_newlines("keep\u2028unicode\tand\x00bytes") == "keep\u2028unicode\tand\x00bytes"
    try:
        normalize_newlines(None)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string input should raise TypeError")
    print("NormalizeNewlines self-check passed")
