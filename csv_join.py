"""Streaming CSV equijoin with an in-memory index over the right-hand input.

The right input is indexed once; rows from the left input are then consumed and
emitted incrementally. Duplicate keys produce the Cartesian expansion for each
matching key while preserving left-row and right-match input order.
"""

import csv
from typing import Dict, Iterable, Iterator, TextIO


Row = Dict[str, str]


def _reader(stream: TextIO, label: str) -> tuple[csv.DictReader, list[str]]:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    if fields is None:
        raise ValueError(f"{label} input is missing a header")
    if len(fields) != len(set(fields)):
        raise ValueError(f"{label} input has duplicate column names")
    return reader, fields


def join_csv(
    left: TextIO,
    right: TextIO,
    left_key: str,
    right_key: str,
) -> Iterator[Row]:
    """Yield matching rows, combining non-colliding columns from both CSVs.

    Column names must be unique across the two inputs, including their key
    columns. Missing key columns, duplicate headers, or malformed row widths
    raise ``ValueError``. The right-hand side is indexed in memory; the left
    side is read lazily, so memory use does not grow with its row count.
    """
    left_reader, left_fields = _reader(left, "left")
    right_reader, right_fields = _reader(right, "right")
    if left_key not in left_fields:
        raise ValueError(f"left key column not found: {left_key}")
    if right_key not in right_fields:
        raise ValueError(f"right key column not found: {right_key}")
    collisions = set(left_fields) & set(right_fields)
    if collisions:
        raise ValueError(f"colliding columns: {', '.join(sorted(collisions))}")

    index: dict[str, list[Row]] = {}
    for row in right_reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("right input row width does not match header")
        index.setdefault(row[right_key], []).append(row)

    for row in left_reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("left input row width does not match header")
        for match in index.get(row[left_key], ()):
            yield {**row, **match}
