import random
from collections import deque

WIDTH = 31   # odd number
HEIGHT = 21  # odd number

maze = [["#"] * WIDTH for _ in range(HEIGHT)]

def generate_maze():
    stack = [(1, 1)]
    maze[1][1] = " "

    while stack:
        x, y = stack[-1]
        neighbors = []

        for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx < WIDTH - 1 and 1 <= ny < HEIGHT - 1 and maze[ny][nx] == "#":
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y + dy // 2][x + dx // 2] = " "
            maze[ny][nx] = " "
            stack.append((nx, ny))
        else:
            stack.pop()

def solve_maze():
    start = (1, 1)
    end = (WIDTH - 2, HEIGHT - 2)

    q = deque([start])
    prev = {start: None}

    while q:
        x, y = q.popleft()

        if (x, y) == end:
            break

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                if maze[ny][nx] in (" ", "E") and (nx, ny) not in prev:
                    prev[(nx, ny)] = (x, y)
                    q.append((nx, ny))

    cur = end
    while cur in prev and prev[cur] is not None:
        if cur != end and cur != start:
            x, y = cur
            maze[y][x] = "."
        cur = prev[cur]

generate_maze()

maze[1][1] = "S"
maze[HEIGHT - 2][WIDTH - 2] = "E"

solve_maze()

print("=== RANDOM MAZE ===")
for row in maze:
    print("".join(row))
