"""Select non-overlapping intervals using a weighted dynamic program."""
from dataclasses import dataclass
from bisect import bisect_right


@dataclass(frozen=True)
class Interval:
    start: int
    end: int
    weight: float
    label: str = ""

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("interval end must be greater than start")


def select_intervals(intervals: list[Interval]) -> list[Interval]:
    """Return a maximum-weight compatible subset, preserving chronological order."""
    ordered = sorted(intervals, key=lambda item: (item.end, item.start))
    ends = [item.end for item in ordered]
    predecessor = [bisect_right(ends, item.start, 0, index) - 1
                   for index, item in enumerate(ordered)]
    best = [0.0] * (len(ordered) + 1)

    for index, item in enumerate(ordered, start=1):
        include = item.weight + best[predecessor[index - 1] + 1]
        best[index] = max(best[index - 1], include)

    chosen: list[Interval] = []
    cursor = len(ordered)
    while cursor:
        item = ordered[cursor - 1]
        include = item.weight + best[predecessor[cursor - 1] + 1]
        if include >= best[cursor - 1]:
            chosen.append(item)
            cursor = predecessor[cursor - 1] + 1
        else:
            cursor -= 1
    return list(reversed(chosen))


if __name__ == "__main__":
    sample = [Interval(0, 3, 5, "design"), Interval(3, 7, 4, "build"),
              Interval(1, 5, 8, "review")]
    print([item.label for item in select_intervals(sample)])
