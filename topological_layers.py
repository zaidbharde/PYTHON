"""Build parallelizable layers from a directed dependency graph."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping


def dependency_layers(graph: Mapping[str, Iterable[str]]) -> list[list[str]]:
    """Return layers where every dependency appears in an earlier layer."""
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)
    outgoing: dict[str, set[str]] = defaultdict(set)
    indegree = {node: 0 for node in nodes}
    for node, dependencies in graph.items():
        for dependency in set(dependencies):
            if node not in outgoing[dependency]:
                outgoing[dependency].add(node)
                indegree[node] += 1
    layers: list[list[str]] = []
    ready = sorted(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        layer = ready
        layers.append(layer)
        visited += len(layer)
        next_ready: list[str] = []
        for node in layer:
            for dependent in sorted(outgoing[node]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)
        ready = sorted(next_ready)
    if visited != len(nodes):
        raise ValueError("dependency graph contains a cycle")
    return layers


if __name__ == "__main__":
    plan = {"compile": ["fetch"], "test": ["compile"], "fetch": [], "lint": []}
    print(dependency_layers(plan))
