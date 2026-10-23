"""Strict, bounded JSON-lines reader for ingestion jobs."""
import json
from collections.abc import Iterable, Iterator
from typing import Any


class JsonLineError(ValueError):
    """A JSON-lines record failed validation."""


def records(lines: Iterable[str], limit: int | None = None) -> Iterator[dict[str, Any]]:
    """Yield object records and identify the exact bad input line."""
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    emitted = 0
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise JsonLineError(f"line {number}: invalid JSON") from exc
        if not isinstance(value, dict):
            raise JsonLineError(f"line {number}: expected an object")
        yield value
        emitted += 1
        if limit is not None and emitted >= limit:
            return


def load(text: str, limit: int | None = None) -> list[dict[str, Any]]:
    return list(records(text.splitlines(), limit))


if __name__ == "__main__":
    print(load('{"ok": true}\n{"count": 2}'))
