import csv
from dataclasses import dataclass
from io import TextIOBase


@dataclass(frozen=True)
class ColumnStats:
    name: str
    count: int
    minimum: float
    maximum: float
    average: float


def read_rows(stream: TextIOBase, required: set[str]) -> list[dict[str, str]]:
    reader = csv.DictReader(stream)
    fields = set(reader.fieldnames or [])
    missing = required - fields
    if missing:
        raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
    return list(reader)


def numeric_stats(rows: list[dict[str, str]], column: str) -> ColumnStats:
    values = [float(row[column]) for row in rows if row.get(column, "").strip()]
    if not values:
        raise ValueError(f"no numeric values found for {column}")
    return ColumnStats(column, len(values), min(values), max(values), sum(values) / len(values))


if __name__ == "__main__":
    from io import StringIO
    rows = read_rows(StringIO("name,score\na,8\nb,10\n"), {"name", "score"})
    print(numeric_stats(rows, "score"))
