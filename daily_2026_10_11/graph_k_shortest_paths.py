"""Compute a small set of shortest simple paths with a best-first search."""
from heapq import heappop, heappush
from typing import Hashable, Iterable


Node = Hashable
Edge = tuple[Node, float]


def k_shortest_paths(graph: dict[Node, Iterable[Edge]], source: Node,
                     target: Node, limit: int = 3) -> list[tuple[float, list[Node]]]:
    """Return up to limit loop-free paths ordered by total cost."""
    if limit < 1:
        raise ValueError("limit must be positive")
    queue: list[tuple[float, tuple[Node, ...]]] = [(0.0, (source,))]
    results: list[tuple[float, list[Node]]] = []
    while queue and len(results) < limit:
        cost, path = heappop(queue)
        current = path[-1]
        if current == target:
            results.append((cost, list(path)))
            continue
        for neighbor, edge_cost in graph.get(current, ()):
            if edge_cost < 0:
                raise ValueError("negative edge costs are unsupported")
            if neighbor not in path:
                heappush(queue, (cost + edge_cost, path + (neighbor,)))
    return results


def path_cost(graph: dict[Node, Iterable[Edge]], path: list[Node]) -> float:
    """Validate a path and calculate its cost from the graph edges."""
    total = 0.0
    for start, end in zip(path, path[1:]):
        choices = {node: weight for node, weight in graph.get(start, ())}
        if end not in choices:
            raise ValueError(f"missing edge from {start!r} to {end!r}")
        total += choices[end]
    return total


if __name__ == "__main__":
    network = {"a": [("b", 2), ("c", 1)], "b": [("d", 2)], "c": [("d", 3)], "d": []}
    print(k_shortest_paths(network, "a", "d", 2))
