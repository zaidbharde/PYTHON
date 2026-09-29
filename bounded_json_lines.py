"""Parse JSON Lines while enforcing a record and byte budget."""

import json
from collections.abc import Iterable, Iterator
from typing import Any


def bounded_records(
    lines: Iterable[str], max_records: int, max_bytes: int
) -> Iterator[dict[str, Any]]:
    """Yield valid object records until either configured budget is exhausted."""
    if max_records < 0 or max_bytes < 0:
        raise ValueError("budgets must be non-negative")
    used_records = 0
    used_bytes = 0
    for line in lines:
        raw = line.strip()
        if not raw:
            continue
        size = len(raw.encode("utf-8"))
        if used_records >= max_records or used_bytes + size > max_bytes:
            return
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("each JSON line must contain an object")
        used_records += 1
        used_bytes += size
        yield value


if __name__ == "__main__":
    sample = ['{"id": 1}', '{"id": 2}']
    print(list(bounded_records(sample, max_records=4, max_bytes=64)))
