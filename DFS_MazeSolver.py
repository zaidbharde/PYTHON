from typing import Optional

Grid = list[list[int]]

def solve_maze(maze: Grid) -> Optional[Grid]:
    """
    Return a solution grid with 1s marking the path,
    or None if no path exists.
    """
    if not maze or not maze[0]:
        raise ValueError("Maze must be a non-empty 2D grid.")

    rows, cols = len(maze), len(maze[0])

    if any(len(row) != cols for row in maze):
        raise ValueError("Maze must be rectangular.")

    if maze[0][0] != 1 or maze[rows - 1][cols - 1] != 1:
        return None

    solution = [[0] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    # down, right, up, left
    directions = ((1, 0), (0, 1), (-1, 0), (0, -1))

    def backtrack(r: int, c: int) -> bool:
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if maze[r][c] == 0 or visited[r][c]:
            return False

        visited[r][c] = True
        solution[r][c] = 1

        if (r, c) == (rows - 1, cols - 1):
            return True

        for dr, dc in directions:
            if backtrack(r + dr, c + dc):
                return True

        solution[r][c] = 0
        return False

    return solution if backtrack(0, 0) else None


def print_grid(grid: Grid) -> None:
    for row in grid:
        print(" ".join(map(str, row)))


def run_maze_solver() -> None:
    maze = [
        [1, 0, 0, 0],
        [1, 1, 0, 1],
        [0, 1, 0, 0],
        [1, 1, 1, 1]
    ]

    solution = solve_maze(maze)

    if solution is None:
        print("No path found.")
    else:
        print("Solution path:")
        print_grid(solution)


if __name__ == "__main__":
    run_maze_solver()
