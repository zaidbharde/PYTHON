def has_cycle(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    for i in range(n):
        if color[i] == WHITE:
            if dfs(i):
                return True
    return False


if __name__ == "__main__":
    graph_with_cycle = {0: [1], 1: [2], 2: [0]}
    graph_no_cycle = {0: [1], 1: [2], 2: [3]}

    print("Graph 1 has cycle:", has_cycle(graph_with_cycle, 3))
    print("Graph 2 has cycle:", has_cycle(graph_no_cycle, 4))
