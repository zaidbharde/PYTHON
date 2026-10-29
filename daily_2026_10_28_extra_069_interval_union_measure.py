"""Measure covered length and uncovered gaps inside a bounded integer domain.

Intervals and the domain use half-open [start, end) semantics.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class IntervalUnionMeasure:
    """Coverage summary for intervals clipped to ``[lower, upper)``."""
    lower: int
    upper: int
    merged: tuple[tuple[int, int], ...]
    union_length: int
    gaps: tuple[tuple[int, int], ...]

    @classmethod
    def calculate(cls, intervals: Iterable[tuple[int, int]],
                  lower: int, upper: int) -> "IntervalUnionMeasure":
        if not isinstance(lower, int) or not isinstance(upper, int):
            raise TypeError("domain bounds must be integers")
        if lower > upper:
            raise ValueError("domain lower bound exceeds upper bound")
        clipped = []
        for pair in intervals:
            try:
                start, end = pair
            except (TypeError, ValueError) as exc:
                raise ValueError("each interval must contain exactly two bounds") from exc
            if not isinstance(start, int) or not isinstance(end, int):
                raise TypeError("interval bounds must be integers")
            if start > end:
                raise ValueError("interval start exceeds end")
            a, b = max(lower, start), min(upper, end)
            if a < b:
                clipped.append((a, b))
        merged: list[tuple[int, int]] = []
        for start, end in sorted(clipped):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        gaps, cursor = [], lower
        for start, end in merged:
            if cursor < start:
                gaps.append((cursor, start))
            cursor = end
        if cursor < upper:
            gaps.append((cursor, upper))
        return cls(lower, upper, tuple(merged),
                   sum(end - start for start, end in merged), tuple(gaps))


if __name__ == "__main__":
    result = IntervalUnionMeasure.calculate([(1, 4), (3, 7), (10, 12)], 0, 13)
    assert result.merged == ((1, 7), (10, 12))
    assert result.union_length == 8
    assert result.gaps == ((0, 1), (7, 10), (12, 13))
    assert IntervalUnionMeasure.calculate([], 4, 4).gaps == ()
    try:
        IntervalUnionMeasure.calculate([(3, 2)], 0, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("reversed interval was accepted")
    print("interval union measure checks passed")
