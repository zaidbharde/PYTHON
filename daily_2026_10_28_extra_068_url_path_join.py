"""Join URL path segments while preserving the URL's scheme, query, and fragment."""
from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def url_path_join(url: str, *segments: str) -> str:
    """Append path segments to a URL without treating its query as part of the path.

    Leading/trailing slashes on supplied segments and duplicate path separators
    are normalized. Each argument represents one segment; embedded separators,
    query/fragment delimiters, and non-string values are rejected.
    """
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not isinstance(segments, tuple):
        raise TypeError("segments must be provided as positional strings")
    parts = urlsplit(url)
    path_parts = [parts.path.strip("/")] if parts.path.strip("/") else []
    for segment in segments:
        if not isinstance(segment, str):
            raise TypeError("each path segment must be a string")
        value = segment.strip("/")
        if any(char in value for char in "?#"):
            raise ValueError("path segments cannot contain query or fragment delimiters")
        if "/" in value or "\\" in value:
            raise ValueError("each argument must be a single path segment")
        if value:
            path_parts.append(value)
    path = "/".join(path_parts)
    if parts.path.startswith("/"):
        path = "/" + path
    if parts.netloc and not path:
        path = "/"
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


if __name__ == "__main__":
    assert url_path_join("https://example.test/api?x=1#top", "/users/", "42") == \
        "https://example.test/api/users/42?x=1#top"
    assert url_path_join("https://example.test", "v1") == "https://example.test/v1"
    assert url_path_join("/root/", "child") == "/root/child"
    assert url_path_join("https://example.test/a?", "b") == "https://example.test/a/b"
    assert url_path_join("", "") == ""
    for invalid in (None, 42):
        try:
            url_path_join("https://example.test", invalid)  # type: ignore[arg-type]
        except TypeError:
            pass
        else:
            raise AssertionError("non-string segment accepted")
    for invalid in ("a/b", "a?b", "a#b", "a\\b"):
        try:
            url_path_join("https://example.test", invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid segment accepted: {invalid!r}")
    print("UrlPathJoin self-check passed")
