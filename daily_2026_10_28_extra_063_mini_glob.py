"""Match strings with a tiny glob grammar: ``*``, ``?``, and backslash escapes."""
import re


def _compile_glob(pattern: str) -> re.Pattern[str]:
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a string")
    pieces: list[str] = ["\\A"]
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char == "\\":
            i += 1
            if i == len(pattern):
                raise ValueError("trailing backslash in glob pattern")
            pieces.append(re.escape(pattern[i]))
        elif char == "*":
            pieces.append(".*")
        elif char == "?":
            pieces.append(".")
        else:
            pieces.append(re.escape(char))
        i += 1
    pieces.append("\\Z")
    return re.compile("".join(pieces), re.DOTALL)


def matches(text: str, pattern: str) -> bool:
    """Return whether *text* fully matches *pattern*; matching is case-sensitive."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return _compile_glob(pattern).fullmatch(text) is not None


if __name__ == "__main__":
    assert matches("report.txt", "*.txt")
    assert matches("a\nb", "a*b")
    assert matches("cat", "c?t") and not matches("coat", "c?t")
    assert matches("*?\\", r"\*\?\\")
    assert matches("", "*") and not matches("x", "")
    try:
        matches("x", "bad\\")
    except ValueError:
        pass
    else:
        raise AssertionError("trailing escape must be rejected")
    try:
        matches(1, "*")  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string text must be rejected")
