"""Topologically order a graph while preserving lexical tie-breaking."""
from __future__ import annotations

import heapq
from collections import defaultdict
from typing import Iterable


def stable_topological_sort(
    nodes: Iterable[str], edges: Iterable[tuple[str, str]]
) -> list[str]:
    """Return a deterministic order or raise ValueError when cyclic."""
    names = set(nodes)
    outgoing: dict[str, set[str]] = defaultdict(set)
    indegree = {name: 0 for name in names}
    for source, target in edges:
        names.update((source, target))
        if target not in outgoing[source]:
            outgoing[source].add(target)
            indegree[target] = indegree.get(target, 0) + 1
            indegree.setdefault(source, 0)
    ready = [name for name in names if indegree.get(name, 0) == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for target in sorted(outgoing[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                heapq.heappush(ready, target)
    if len(order) != len(names):
        blocked = sorted(names.difference(order))
        raise ValueError(f"graph contains a cycle involving {blocked}")
    return order


def dependency_levels(order: list[str], edges: Iterable[tuple[str, str]]) -> dict[str, int]:
    """Calculate the earliest executable level for each ordered node."""
    parents: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        parents[target].append(source)
    levels: dict[str, int] = {}
    for node in order:
        levels[node] = 0 if not parents[node] else 1 + max(levels[parent] for parent in parents[node])
    return levels


if __name__ == "__main__":
    graph = [("fetch", "parse"), ("parse", "store"), ("fetch", "validate")]
    order = stable_topological_sort(["store", "fetch", "parse", "validate"], graph)
    assert order == ["fetch", "parse", "store", "validate"]
    assert dependency_levels(order, graph)["store"] == 2
    print("topological sort checks passed")
