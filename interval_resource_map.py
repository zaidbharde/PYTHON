"""Assign non-overlapping intervals to the earliest available resource."""
from __future__ import annotations

import heapq
from collections.abc import Iterable


def assign_resources(intervals: Iterable[tuple[int, int]]) -> list[int]:
    """Return a resource identifier for each interval in input order."""
    indexed = sorted(enumerate(intervals), key=lambda item: (item[1][0], item[1][1]))
    available: list[tuple[int, int]] = []
    next_resource = 0
    assignments = [0] * len(indexed)
    for original, (start, finish) in indexed:
        if finish < start:
            raise ValueError("interval finish precedes start")
        while available and available[0][0] <= start:
            _, resource = heapq.heappop(available)
            heapq.heappush(available, (start, resource))
        if available and available[0][0] == start:
            end, resource = heapq.heappop(available)
            assignments[original] = resource
            heapq.heappush(available, (finish, resource))
        else:
            resource = next_resource
            next_resource += 1
            assignments[original] = resource
            heapq.heappush(available, (finish, resource))
    return assignments


if __name__ == "__main__":
    print(assign_resources([(0, 4), (1, 2), (4, 8), (2, 5)]))
