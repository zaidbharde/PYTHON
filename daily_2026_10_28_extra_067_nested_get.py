"""Read a value from nested mappings using explicit path segments and a miss value."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

_MISSING = TypeVar("_MISSING")


def nested_get(
    mapping: Mapping[Any, Any], path: Iterable[Any], missing: _MISSING
) -> Any | _MISSING:
    """Traverse mapping keys in ``path``; return ``missing`` if any key is absent.

    ``path`` is an iterable of literal keys (not a dotted string). An empty path
    selects the original mapping. Non-mapping intermediate values are treated
    as misses, while invalid root/path arguments raise ``TypeError``.
    """
    if not isinstance(mapping, Mapping):
        raise TypeError("mapping must implement collections.abc.Mapping")
    if isinstance(path, (str, bytes)) or not isinstance(path, Iterable):
        raise TypeError("path must be an iterable of key segments, not text")
    current: Any = mapping
    for key in path:
        if not isinstance(current, Mapping):
            return missing
        try:
            current = current[key]
        except KeyError:
            return missing
        except TypeError as error:
            raise TypeError("path segments must be valid mapping keys") from error
    return current


if __name__ == "__main__":
    data = {"account": {"name": "Ada", "settings": {"theme": "dark"}}, "none": None}
    absent = object()
    assert nested_get(data, ("account", "settings", "theme"), absent) == "dark"
    assert nested_get(data, ("account", "missing"), absent) is absent
    assert nested_get(data, ("account", "name", "extra"), absent) is absent
    assert nested_get(data, ("none",), absent) is None
    assert nested_get(data, (), absent) is data
    for bad_path in ("account.name", b"account", None):
        try:
            nested_get(data, bad_path, absent)  # type: ignore[arg-type]
        except TypeError:
            pass
        else:
            raise AssertionError("invalid path accepted")
    print("NestedGet self-check passed")
