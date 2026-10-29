"""Render rectangular rows as aligned, readable plain-text columns."""
from collections.abc import Iterable, Sequence


class TableFormatter:
    """Format rows with optional headings and per-column alignment."""

    @staticmethod
    def format(rows: Iterable[Sequence[object]], headers: Sequence[object] | None = None,
               align: str = "left", gap: int = 2) -> str:
        if align not in {"left", "right", "center"}:
            raise ValueError("align must be 'left', 'right', or 'center'")
        if not isinstance(gap, int) or isinstance(gap, bool) or gap < 0:
            raise ValueError("gap must be a non-negative integer")
        data: list[list[str]] = []
        for row in rows:
            if isinstance(row, (str, bytes)):
                raise ValueError("each row must be a sequence of cells")
            cells = [str(cell) for cell in row]
            if any("\n" in cell or "\r" in cell for cell in cells):
                raise ValueError("cells must not contain line breaks")
            data.append(cells)
        heading = None if headers is None else [str(cell) for cell in headers]
        if heading is not None and any("\n" in cell or "\r" in cell for cell in heading):
            raise ValueError("headers must not contain line breaks")
        width = len(heading) if heading is not None else (len(data[0]) if data else 0)
        if heading is not None and width == 0:
            raise ValueError("headers must contain at least one column")
        if any(len(row) != width for row in data):
            raise ValueError("all rows must match the number of columns")
        if width == 0:
            return ""
        all_rows = ([heading] if heading is not None else []) + data
        widths = [max(len(row[i]) for row in all_rows) for i in range(width)]
        def render(row: list[str]) -> str:
            method = {"left": str.ljust, "right": str.rjust, "center": str.center}[align]
            cells = [method(cell, widths[i]) for i, cell in enumerate(row)]
            return (" " * gap).join(cells).rstrip()
        output: list[str] = []
        if heading is not None:
            output.extend((render(heading), (" " * gap).join("-" * size for size in widths)))
        output.extend(render(row) for row in data)
        return "\n".join(output)


if __name__ == "__main__":
    sample = TableFormatter.format([["Ada", 7], ["Grace", 12]], ["Name", "Count"], align="right")
    assert sample == " Name  Count\n-----  -----\n  Ada      7\nGrace     12"
    assert TableFormatter.format([["x", "long"], ["yy", "z"]]) == "x   long\nyy  z"
    assert TableFormatter.format([]) == ""
    for bad_rows in ([["a"], ["b", "c"]], ["not a row"]):
        try:
            TableFormatter.format(bad_rows)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid rows were accepted")
    print("TableFormatter self-check passed")
