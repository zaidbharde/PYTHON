"""Flatten nested mappings into dotted paths with escaped separators."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def flatten_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return scalar leaves as dotted paths, escaping ``\\`` and ``.`` in keys.

    Empty nested mappings are retained as leaf values; an empty root yields {}.
    All mapping keys must be strings so paths remain unambiguous.
    """
    if not isinstance(value, Mapping):
        raise TypeError("value must be a mapping")
    flattened: dict[str, Any] = {}

    def visit(mapping: Mapping[str, Any], prefix: str) -> None:
        if not mapping and prefix:
            flattened[prefix] = {}
            return
        for key, item in mapping.items():
            if not isinstance(key, str):
                raise TypeError("mapping keys must be strings")
            segment = key.replace("\\", "\\\\").replace(".", "\\.")
            path = f"{prefix}.{segment}" if prefix else segment
            if isinstance(item, Mapping):
                visit(item, path)
            else:
                flattened[path] = item

    visit(value, "")
    return flattened


if __name__ == "__main__":
    sample = {"profile.name": "Ada", "settings": {"theme": "dark", "empty": {}}}
    assert flatten_mapping(sample) == {
        r"profile\.name": "Ada",
        "settings.theme": "dark",
        "settings.empty": {},
    }
    assert flatten_mapping({}) == {}
    assert flatten_mapping({"a\\b": 1}) == {r"a\\b": 1}
    try:
        flatten_mapping({1: "invalid"})
    except TypeError:
        pass
    else:
        raise AssertionError("non-string keys must be rejected")
    print("NestedMappingFlatten self-check passed")
