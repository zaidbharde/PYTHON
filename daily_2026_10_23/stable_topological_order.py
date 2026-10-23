"""Deterministic topological ordering with useful cycle diagnostics."""
from collections import defaultdict, deque
from typing import Hashable, Iterable


def order_tasks(edges: Iterable[tuple[Hashable, Hashable]]) -> list[Hashable]:
    """Return a stable order, or raise ValueError with the cyclic nodes."""
    graph: dict[Hashable, set[Hashable]] = defaultdict(set)
    indegree: dict[Hashable, int] = {}
    for before, after in edges:
        graph[before].add(after)
        graph.setdefault(after, set())
        indegree.setdefault(before, 0)
        indegree[after] = indegree.get(after, 0) + 1
    ready = deque(sorted((node for node, degree in indegree.items() if degree == 0), key=repr))
    result: list[Hashable] = []
    while ready:
        node = ready.popleft()
        result.append(node)
        for child in sorted(graph[node], key=repr):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    if len(result) != len(indegree):
        cycle = sorted((node for node, degree in indegree.items() if degree), key=repr)
        raise ValueError(f"dependency cycle includes: {cycle}")
    return result


if __name__ == "__main__":
    print(order_tasks([("fetch", "parse"), ("parse", "report")]))
