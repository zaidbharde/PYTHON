"""Allocate a finite retry budget across jobs by priority."""
from dataclasses import dataclass
import heapq


@dataclass(order=True)
class _Candidate:
    priority: int
    name: str
    requested: int


def allocate_budgets(requests: dict[str, int], budget: int, priorities: dict[str, int] | None = None) -> dict[str, int]:
    if budget < 0 or any(amount < 0 for amount in requests.values()):
        raise ValueError("budget and requests must be non-negative")
    priorities = priorities or {}
    queue = [_Candidate(priorities.get(name, 0), name, amount) for name, amount in requests.items()]
    heapq.heapify(queue)
    result = {name: 0 for name in requests}
    while queue and budget:
        candidate = heapq.heappop(queue)
        result[candidate.name] += 1
        budget -= 1
        candidate.requested -= 1
        if candidate.requested:
            heapq.heappush(queue, candidate)
    return result
