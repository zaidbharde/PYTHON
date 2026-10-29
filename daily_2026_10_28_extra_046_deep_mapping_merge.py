"""Deep-merge mappings, recursively combining mappings and concatenating lists."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def deep_mapping_merge(base: Mapping[Any, Any], update: Mapping[Any, Any]) -> dict[Any, Any]:
    """Return a copy combining nested mappings; lists append, other values replace.

    Neither input is mutated. A value whose type differs from the existing value
    replaces it, except that two lists are concatenated.
    """
    if not isinstance(base, Mapping) or not isinstance(update, Mapping):
        raise TypeError("base and update must be mappings")

    result = deepcopy(dict(base))
    for key, value in update.items():
        previous = result.get(key)
        if isinstance(previous, Mapping) and isinstance(value, Mapping):
            result[key] = deep_mapping_merge(previous, value)
        elif isinstance(previous, list) and isinstance(value, list):
            result[key] = deepcopy(previous) + deepcopy(value)
        else:
            result[key] = deepcopy(value)
    return result


if __name__ == "__main__":
    original = {"service": {"host": "localhost", "ports": [8000]}, "debug": False}
    merged = deep_mapping_merge(original, {"service": {"ports": [9000], "tls": True}})
    assert merged == {
        "service": {"host": "localhost", "ports": [8000, 9000], "tls": True},
        "debug": False,
    }
    assert original["service"]["ports"] == [8000]
    try:
        deep_mapping_merge({}, [])
    except TypeError:
        pass
    else:
        raise AssertionError("non-mapping update must be rejected")
    print("deep mapping merge checks passed")
