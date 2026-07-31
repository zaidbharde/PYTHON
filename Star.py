import math, time, os

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def galaxy():
    w, h = 80, 24
    cx, cy = w // 2, h // 2
    stars = [(math.cos(a)*r, math.sin(a)*r) for r in range(2, 12) for a in [i * math.pi/4 for i in range(8)]]

    while True:
        clear()
        t = time.time()
        grid = [[' ' for _ in range(w)] for _ in range(h)]
        for x0, y0 in stars:
            angle = t
            x = int(cx + x0 * math.cos(angle) - y0 * math.sin(angle))
            y = int(cy + x0 * math.sin(angle) + y0 * math.cos(angle))
            if 0 <= x < w and 0 <= y < h:
                grid[y][x] = '*'
        for row in grid:
            print(''.join(row))
        time.sleep(0.07)

try:
    galaxy()
except KeyboardInterrupt:
    print("\nOut of orbit.")
