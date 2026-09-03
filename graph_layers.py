from collections import defaultdict, deque
from typing import Hashable, Iterable


def dependency_layers(edges: Iterable[tuple[Hashable, Hashable]]) -> list[list[Hashable]]:
    """Return executable layers, or raise ValueError when dependencies cycle."""
    outgoing: dict[Hashable, set[Hashable]] = defaultdict(set)
    indegree: dict[Hashable, int] = defaultdict(int)
    for prerequisite, task in edges:
        indegree.setdefault(prerequisite, 0)
        if task not in outgoing[prerequisite]:
            outgoing[prerequisite].add(task)
            indegree[task] += 1
    ready = deque(sorted((node for node, degree in indegree.items() if degree == 0), key=str))
    layers: list[list[Hashable]] = []
    visited = 0
    while ready:
        layer = list(ready)
        ready.clear()
        layers.append(layer)
        for node in layer:
            visited += 1
            for dependent in sorted(outgoing[node], key=str):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
    if visited != len(indegree):
        raise ValueError("dependency graph contains a cycle")
    return layers


if __name__ == "__main__":
    graph = [("fetch", "parse"), ("parse", "index"), ("fetch", "archive")]
    print(dependency_layers(graph))
