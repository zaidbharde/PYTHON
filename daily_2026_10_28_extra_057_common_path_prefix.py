"""Find the longest shared filesystem path prefix without splitting components."""

import os
from collections.abc import Iterable


def common_path_prefix(paths: Iterable[str]) -> str:
    """Return the normalized shared path, or ``""`` for no paths.

    Like :func:`os.path.commonpath`, this compares whole path components and
    raises ``ValueError`` when paths use incompatible roots or path styles.
    """
    items = list(paths)
    if not items:
        return ""
    if any(not isinstance(path, str) for path in items):
        raise TypeError("all paths must be strings")
    if any("\0" in path for path in items):
        raise ValueError("paths cannot contain NUL characters")
    return os.path.commonpath(items)


if __name__ == "__main__":
    assert common_path_prefix(["/var/log/app", "/var/log/archive"]) == "/var/log"
    assert common_path_prefix(["/usr/bin", "/usr/lib"]) == "/usr"
    assert common_path_prefix(["/alpha", "/alpine"]) == "/"
    assert common_path_prefix(["docs/one", "docs/two/file"]) == "docs"
    assert common_path_prefix(["single/path"]) == "single/path"
    assert common_path_prefix([]) == ""
    try:
        common_path_prefix(["/root", "relative/path"])
    except ValueError:
        pass
    else:
        raise AssertionError("incompatible roots should fail")
    try:
        common_path_prefix(["valid", 42])  # type: ignore[list-item]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string paths should fail")
    print("common_path_prefix self-checks passed")
