"""Find every substring occurrence, including matches that overlap."""

def overlapping_matches(text: str, pattern: str) -> list[int]:
    """Return start indices of pattern in text using KMP in O(n + m) time.

    An empty pattern matches at every boundary, including the end of text.
    """
    if not isinstance(text, str) or not isinstance(pattern, str):
        raise TypeError("text and pattern must be strings")
    if not pattern:
        return list(range(len(text) + 1))

    # Build the longest proper-prefix/suffix table for the pattern.
    prefix = [0] * len(pattern)
    matched = 0
    for i in range(1, len(pattern)):
        while matched and pattern[i] != pattern[matched]:
            matched = prefix[matched - 1]
        if pattern[i] == pattern[matched]:
            matched += 1
            prefix[i] = matched

    starts: list[int] = []
    matched = 0
    for i, char in enumerate(text):
        while matched and char != pattern[matched]:
            matched = prefix[matched - 1]
        if char == pattern[matched]:
            matched += 1
            if matched == len(pattern):
                starts.append(i - len(pattern) + 1)
                matched = prefix[matched - 1]  # retain suffix for overlaps
    return starts


if __name__ == "__main__":
    assert overlapping_matches("bananana", "ana") == [1, 3, 5]
    assert overlapping_matches("aaaa", "aa") == [0, 1, 2]
    assert overlapping_matches("abc", "") == [0, 1, 2, 3]
    assert overlapping_matches("abc", "z") == []
    assert overlapping_matches("", "a") == []
    try:
        overlapping_matches("abc", None)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string pattern should be rejected")
    print("overlapping_matches self-check passed")
