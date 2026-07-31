W, H = 40, 20
grid = [[0]*W for _ in range(H)]
x, y, d = W//2, H//2, 0
dirs = [(0,-1),(1,0),(0,1),(-1,0)]

for _ in range(500):
    grid[y][x] = 1 - grid[y][x]
