"""Incremental JSON-lines batching without loading an entire stream."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, TextIO
from typing import Any


def read_batches(stream: TextIO, batch_size: int) -> Iterator[list[dict[str, Any]]]:
    """Yield validated object batches while preserving input order."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    batch: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(stream, start=1):
        text = raw_line.strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {line_number}") from error
        if not isinstance(value, dict):
            raise TypeError(f"line {line_number} is not a JSON object")
        batch.append(value)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def flatten_batches(batches: Iterable[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Materialize batches for callers that need a regular list."""
    return [item for batch in batches for item in batch]
