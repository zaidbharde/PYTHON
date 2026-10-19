"""Assign tasks to the earliest executable layer in a dependency DAG."""

from __future__ import annotations

from collections import defaultdict, deque


def dependency_layers(tasks: list[str], dependencies: list[tuple[str, str]]) -> list[list[str]]:
    children: dict[str, list[str]] = defaultdict(list)
    remaining = {task: 0 for task in tasks}
    for prerequisite, dependent in dependencies:
        if prerequisite not in remaining or dependent not in remaining:
            raise ValueError("dependency names must appear in tasks")
        children[prerequisite].append(dependent)
        remaining[dependent] += 1
    ready = deque(sorted(task for task, count in remaining.items() if count == 0))
    layers: list[list[str]] = []
    completed = 0
    while ready:
        layer = list(ready)
        ready.clear()
        layers.append(layer)
        completed += len(layer)
        for task in layer:
            for dependent in sorted(children[task]):
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)
    if completed != len(tasks):
        raise ValueError("dependencies contain a cycle")
    return layers


if __name__ == "__main__":
    print(dependency_layers(["lint", "test", "build", "deploy"], [("lint", "test"), ("test", "build"), ("build", "deploy")]))
