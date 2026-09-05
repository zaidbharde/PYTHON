"""Compute parallel execution layers for a directed dependency graph."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping


def dependency_layers(graph: Mapping[str, Iterable[str]]) -> list[list[str]]:
    """Return sorted zero-based layers, where each node follows its prerequisites.

    The input maps a node to the nodes it depends on. Nodes mentioned only as
    prerequisites are included automatically, and cycles raise ``ValueError``.
    """
    prerequisites = {node: set(items) for node, items in graph.items()}
    for items in list(prerequisites.values()):
        for item in items:
            prerequisites.setdefault(item, set())
    dependents: dict[str, set[str]] = defaultdict(set)
    remaining = {node: len(items) for node, items in prerequisites.items()}
    for node, items in prerequisites.items():
        for item in items:
            dependents[item].add(node)
    ready = deque(sorted(node for node, count in remaining.items() if count == 0))
    layers: list[list[str]] = []
    processed = 0
    while ready:
        current = sorted(ready)
        ready.clear()
        layers.append(current)
        processed += len(current)
        for node in current:
            for dependent in dependents[node]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)
    if processed != len(remaining):
        cycle_nodes = sorted(node for node, count in remaining.items() if count)
        raise ValueError(f"dependency cycle includes: {', '.join(cycle_nodes)}")
    return layers


if __name__ == "__main__":
    build = {"package": ["test", "compile"], "test": ["compile"], "compile": ["source"]}
    print(dependency_layers(build))
