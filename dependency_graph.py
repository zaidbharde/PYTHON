from collections import defaultdict, deque


def installation_order(dependencies: dict[str, set[str]]) -> list[str]:
    nodes = set(dependencies)
    for required in dependencies.values():
        nodes.update(required)
    outgoing: dict[str, set[str]] = defaultdict(set)
    incoming = {node: 0 for node in nodes}
    for package, required in dependencies.items():
        for prerequisite in required:
            if package not in outgoing[prerequisite]:
                outgoing[prerequisite].add(package)
                incoming[package] += 1
    ready = deque(sorted(node for node, degree in incoming.items() if degree == 0))
    result = []
    while ready:
        current = ready.popleft()
        result.append(current)
        for dependent in sorted(outgoing[current]):
            incoming[dependent] -= 1
            if incoming[dependent] == 0:
                ready.append(dependent)
    if len(result) != len(nodes):
        cycle = sorted(node for node, degree in incoming.items() if degree)
        raise ValueError(f"dependency cycle detected: {cycle}")
    return result


if __name__ == "__main__":
    graph = {"app": {"api", "ui"}, "api": {"core"}, "ui": {"core"}}
    print(installation_order(graph))
