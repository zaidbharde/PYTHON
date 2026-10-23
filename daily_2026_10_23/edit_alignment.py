"""Levenshtein distance with a human-readable optimal edit script."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Edit:
    operation: str
    source: str | None
    target: str | None


def align(source: str, target: str) -> tuple[int, list[Edit]]:
    rows, cols = len(source) + 1, len(target) + 1
    cost = [[0] * cols for _ in range(rows)]
    for row in range(rows):
        cost[row][0] = row
    for col in range(cols):
        cost[0][col] = col
    for row in range(1, rows):
        for col in range(1, cols):
            same = cost[row - 1][col - 1] if source[row - 1] == target[col - 1] else 10**9
            cost[row][col] = min(same, cost[row - 1][col] + 1, cost[row][col - 1] + 1)
    edits: list[Edit] = []
    row, col = len(source), len(target)
    while row or col:
        if row and col and source[row - 1] == target[col - 1] and cost[row][col] == cost[row - 1][col - 1]:
            edits.append(Edit("keep", source[row - 1], target[col - 1]))
            row, col = row - 1, col - 1
        elif row and cost[row][col] == cost[row - 1][col] + 1:
            edits.append(Edit("delete", source[row - 1], None))
            row -= 1
        else:
            edits.append(Edit("insert", None, target[col - 1]))
            col -= 1
    edits.reverse()
    return cost[-1][-1], edits


if __name__ == "__main__":
    print(align("kitten", "sitting")[0])
