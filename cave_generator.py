import random
W, H = 60, 25
grid = [['#' for _ in range(W)] for _ in range(H)]

for _ in range(3000):
    x, y = random.randint(1, W-2), random.randint(1, H-2)
    for _ in range(3):
        grid[y][x] = '.'
        x = max(1, min(W-2, x + random.choice([-1,0,1])))
        y = max(1, min(H-2, y + random.choice([-1,0,1])))

for row in grid: print(''.join(row))
