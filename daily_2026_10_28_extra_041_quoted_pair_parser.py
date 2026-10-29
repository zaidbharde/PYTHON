"""Parse delimited key/value pairs while ignoring separators inside quotes."""


def parse_quoted_pairs(text: str, *, item_separator: str = ",",
                       pair_separator: str = "=", quote: str = '"') -> dict[str, str]:
    """Strip quotes/whitespace; later duplicate keys replace earlier ones.

    Backslash escapes the next character inside quotes; empty items are ignored.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not item_separator or not pair_separator or item_separator == pair_separator:
        raise ValueError("separators must be non-empty and distinct")
    if len(quote) != 1 or quote in item_separator or quote in pair_separator:
        raise ValueError("quote must be one character, distinct from separators")

    result: dict[str, str] = {}
    key, value = [], []
    in_value = quoted = escaped = False

    def finish() -> None:
        nonlocal key, value, in_value
        k, v = "".join(key).strip(), "".join(value).strip()
        if k or v or in_value:
            if not in_value or not k:
                raise ValueError("non-empty items need a non-empty key and pair separator")
            result[k] = v
        key, value, in_value = [], [], False

    i = 0
    while i < len(text):
        c = text[i]
        if escaped:
            (value if in_value else key).append(c)
            escaped = False
            i += 1
            continue
        if quoted and c == "\\":
            escaped = True
            i += 1
            continue
        if c == quote:
            quoted = not quoted
            i += 1
            continue
        if not quoted and text.startswith(item_separator, i):
            finish()
            i += len(item_separator)
            continue
        if not quoted and not in_value and text.startswith(pair_separator, i):
            in_value = True
            i += len(pair_separator)
            continue
        (value if in_value else key).append(c)
        i += 1
    if quoted or escaped:
        raise ValueError("unterminated quote or escape")
    finish()
    return result


if __name__ == "__main__":
    assert parse_quoted_pairs('host="alpha,beta", note="x=y", retries=3') == {
        "host": "alpha,beta", "note": "x=y", "retries": "3"}
    assert parse_quoted_pairs('a="say \\"hi\\"",a=last') == {"a": "last"}
    for bad in ("missing", " =value", 'a="unfinished'):
        try:
            parse_quoted_pairs(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted malformed input: {bad!r}")
    print("quoted pair parser checks passed")
