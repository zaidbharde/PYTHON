"""Plan parallel execution waves for a finite dependency graph."""
from collections import defaultdict
from collections.abc import Iterable


def waves(jobs: Iterable[str], dependencies: Iterable[tuple[str, str]]) -> list[list[str]]:
    """Return lexicographically stable waves, or reject a cyclic graph."""
    names = set(jobs)
    graph: dict[str, set[str]] = defaultdict(set)
    indegree = {name: 0 for name in names}
    for prerequisite, job in dependencies:
        names.update((prerequisite, job))
        graph[prerequisite].add(job)
        indegree.setdefault(prerequisite, 0)
        indegree[job] = indegree.get(job, 0) + 1
    result: list[list[str]] = []
    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    completed = 0
    while ready:
        result.append(ready)
        completed += len(ready)
        next_ready: list[str] = []
        for name in ready:
            for child in graph[name]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    next_ready.append(child)
        ready = sorted(next_ready)
    if completed != len(indegree):
        raise ValueError("dependencies contain a cycle")
    return result


if __name__ == "__main__":
    print(waves(["compile", "test", "package"], [("compile", "test"), ("test", "package")]))
