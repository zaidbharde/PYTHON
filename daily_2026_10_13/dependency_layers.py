"""Build deterministic dependency layers for a directed acyclic graph."""
from collections import defaultdict
from typing import Iterable


def dependency_layers(
    nodes: Iterable[str], edges: Iterable[tuple[str, str]]
) -> list[tuple[str, ...]]:
    """Return batches that can run in parallel, or raise on a cycle."""
    names = set(nodes)
    graph: dict[str, set[str]] = defaultdict(set)
    indegree = {name: 0 for name in names}
    for prerequisite, dependent in edges:
        names.update((prerequisite, dependent))
        graph[prerequisite].add(dependent)
        indegree[dependent] = indegree.get(dependent, 0) + 1
        indegree.setdefault(prerequisite, 0)

    ready = sorted(name for name, count in indegree.items() if count == 0)
    layers: list[tuple[str, ...]] = []
    processed = 0
    while ready:
        current = tuple(ready)
        layers.append(current)
        processed += len(current)
        next_ready: list[str] = []
        for item in current:
            for dependent in sorted(graph[item]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)
        ready = sorted(next_ready)

    if processed != len(indegree):
        blocked = sorted(name for name, count in indegree.items() if count > 0)
        raise ValueError(f"dependency cycle includes: {', '.join(blocked)}")
    return layers


if __name__ == "__main__":
    graph = [("parse", "compile"), ("compile", "package"), ("lint", "package")]
    print(dependency_layers(("parse", "compile", "lint", "package"), graph))
