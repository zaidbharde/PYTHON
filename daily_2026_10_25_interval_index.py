"""A small interval index for overlap lookups over immutable records."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    label: str

    def overlaps(self, start: int, end: int) -> bool:
        return self.start < end and start < self.end


class IntervalIndex:
    def __init__(self, spans: list[Span] | None = None) -> None:
        self._spans = sorted(spans or [], key=lambda span: (span.start, span.end))

    def add(self, span: Span) -> None:
        if span.start >= span.end:
            raise ValueError("span must have a positive width")
        self._spans.append(span)
        self._spans.sort(key=lambda item: (item.start, item.end))

    def query(self, start: int, end: int) -> list[Span]:
        if start >= end:
            return []
        return [span for span in self._spans if span.start >= end or span.overlaps(start, end)]

    def labels(self, start: int, end: int) -> list[str]:
        return [span.label for span in self.query(start, end) if span.overlaps(start, end)]


if __name__ == "__main__":
    index = IntervalIndex([Span(1, 4, "alpha"), Span(6, 9, "beta")])
    print(index.labels(3, 7))
