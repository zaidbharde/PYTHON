"""Deep configuration overlay with explicit handling for deletions."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

_DELETE = object()


def overlay(base: Mapping[str, Any], override: Mapping[str, Any], *, delete: set[str] | None = None) -> dict[str, Any]:
    """Merge nested mappings; lists and scalar values are replaced atomically."""
    removals = delete or set()
    result = deepcopy(dict(base))
    for key, value in override.items():
        if key in removals or value is _DELETE:
            result.pop(key, None)
            continue
        current = result.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            result[key] = overlay(current, value, delete=removals)
        else:
            result[key] = deepcopy(value)
    for key in removals:
        result.pop(key, None)
    return result


if __name__ == "__main__":
    defaults = {"server": {"host": "localhost", "port": 8000}, "debug": False}
    print(overlay(defaults, {"server": {"port": 9000}, "debug": True}))
