"""Flatten nested JSON-like mappings into stable pointer paths."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """Return JSON Pointer-like paths for every scalar leaf."""
    if isinstance(value, Mapping):
        if not value:
            return {prefix: {}} if prefix else {}
        output: dict[str, Any] = {}
        for key in sorted(value, key=str):
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            output.update(flatten(value[key], f"{prefix}/{escaped}"))
        return output
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        output = {}
        if not value:
            return {prefix: []} if prefix else {}
        for index, item in enumerate(value):
            output.update(flatten(item, f"{prefix}/{index}"))
        return output
    return {prefix or "/": value}


def diff_paths(before: Any, after: Any) -> dict[str, tuple[Any, Any]]:
    """Describe added, removed, and changed scalar paths."""
    left, right = flatten(before), flatten(after)
    changes: dict[str, tuple[Any, Any]] = {}
    for path in sorted(set(left) | set(right)):
        old, new = left.get(path), right.get(path)
        if old != new:
            changes[path] = (old, new)
    return changes


if __name__ == "__main__":
    print(diff_paths({"a": [1, 2]}, {"a": [1, 3]}))
