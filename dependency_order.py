"""Stable topological sorting with explicit cycle detection."""

from collections import defaultdict, deque
from collections.abc import Hashable, Iterable


def dependency_order(nodes: Iterable[Hashable], edges: Iterable[tuple[Hashable, Hashable]]) -> list[Hashable]:
    """Return nodes before their dependents, preserving input order when possible."""
    ordered_nodes = list(dict.fromkeys(nodes))
    rank = {node: index for index, node in enumerate(ordered_nodes)}
    graph: dict[Hashable, set[Hashable]] = defaultdict(set)
    indegree = {node: 0 for node in ordered_nodes}
    for source, target in edges:
        if source not in indegree or target not in indegree:
            raise ValueError("edges must reference declared nodes")
        if target not in graph[source]:
            graph[source].add(target)
            indegree[target] += 1
    ready = deque(sorted((node for node, degree in indegree.items() if degree == 0), key=rank.__getitem__))
    result: list[Hashable] = []
    while ready:
        current = ready.popleft()
        result.append(current)
        for dependent in sorted(graph[current], key=rank.__getitem__):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    if len(result) != len(ordered_nodes):
        cycle_members = [node for node, degree in indegree.items() if degree]
        raise ValueError(f"dependency cycle detected: {cycle_members}")
    return result
