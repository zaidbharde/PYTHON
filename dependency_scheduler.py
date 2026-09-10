"""Stable topological scheduling for dependency graphs."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable


def dependency_layers(
    nodes: Iterable[str], edges: Iterable[tuple[str, str]]
) -> list[list[str]]:
    """Return batches in which every prerequisite precedes its dependent."""
    names = set(nodes)
    outgoing: dict[str, set[str]] = defaultdict(set)
    indegree = {name: 0 for name in names}
    for prerequisite, dependent in edges:
        if prerequisite not in names or dependent not in names:
            raise ValueError("edges must reference declared nodes")
        if dependent not in outgoing[prerequisite]:
            outgoing[prerequisite].add(dependent)
            indegree[dependent] += 1

    ready = deque(sorted(name for name, degree in indegree.items() if degree == 0))
    layers: list[list[str]] = []
    visited = 0
    while ready:
        current = sorted(ready)
        ready.clear()
        layers.append(current)
        visited += len(current)
        for name in current:
            for dependent in sorted(outgoing[name]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)

    if visited != len(names):
        raise ValueError("dependency graph contains a cycle")
    return layers


def flatten_layers(layers: list[list[str]]) -> list[str]:
    """Flatten layers while preserving deterministic scheduler order."""
    return [name for layer in layers for name in layer]
