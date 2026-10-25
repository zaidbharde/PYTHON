"""Build deterministic execution layers from a directed dependency graph."""
from collections import defaultdict, deque


def dependency_layers(graph: dict[str, list[str]]) -> list[list[str]]:
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
    ready = deque(sorted(node for node, count in indegree.items() if count == 0))
    layers: list[list[str]] = []
    while ready:
        layer = list(ready)
        layers.append(layer)
        for node in layer:
            for dependent in sorted(outgoing[node]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
    if sum(map(len, layers)) != len(nodes):
        raise ValueError("dependency graph contains a cycle")
    return layers


if __name__ == "__main__":
    plan = {"package": ["compile"], "test": ["package"], "compile": ["source"]}
    print(dependency_layers(plan))
