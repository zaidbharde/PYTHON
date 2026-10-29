"""Canonicalize URL query pairs, sorting pairs while retaining duplicates."""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit

_BAD_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")


def canonical_query(url_or_query: str) -> str:
    """Return a stable, form-encoded query string from a URL or raw query.

    Pairs are sorted by key then value; repeated keys and blank values remain.
    A leading '?' is optional. Malformed percent escapes are rejected.
    """
    if not isinstance(url_or_query, str):
        raise TypeError("url_or_query must be a string")
    if "?" in url_or_query:
        query = urlsplit(url_or_query).query
    else:
        query = url_or_query[1:] if url_or_query.startswith("?") else url_or_query
    if _BAD_ESCAPE.search(query):
        raise ValueError("query contains a malformed percent escape")
    try:
        pairs = parse_qsl(query, keep_blank_values=True, strict_parsing=True,
                          encoding="utf-8", errors="strict")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid query string: {exc}") from exc
    return urlencode(sorted(pairs), doseq=True, encoding="utf-8", errors="strict")


if __name__ == "__main__":
    assert canonical_query("https://example.test/p?z=last&a=one&a=two&empty=") == \
        "a=one&a=two&empty=&z=last"
    assert canonical_query("?b=x+y&a=%C3%A9") == "a=%C3%A9&b=x+y"
    assert canonical_query("") == ""
    for invalid in ("x=%Q0", "a",):
        try:
            canonical_query(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid query accepted: {invalid!r}")
    print("CanonicalQuery self-check passed")
