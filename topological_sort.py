from collections import defaultdict, deque


def topological_sort(edges):
    graph = defaultdict(list)
    indegree = defaultdict(int)
    nodes = set()
    for source, target in edges:
        graph[source].append(target)
        indegree[target] += 1
        nodes.update((source, target))
    queue = deque(sorted(node for node in nodes if indegree[node] == 0))
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return order if len(order) == len(nodes) else []


if __name__ == "__main__":
    plan = [("parse", "compile"), ("compile", "test"), ("parse", "lint")]
    print(topological_sort(plan))
