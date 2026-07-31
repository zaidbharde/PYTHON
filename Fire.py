import os, time, random

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def fire():
    w, h = 60, 20
    chars = ' .:-=+*#%@'
    heat = [[0 for _ in range(w)] for _ in range(h)]

    while True:
        clear()
        for x in range(w):
            heat[h-1][x] = random.randint(0, 9)

        for y in range(h-2, -1, -1):
            for x in range(w):
                total = sum(heat[y2][x2] for x2 in range(max(0,x-1), min(w,x+2))
                                            for y2 in range(y+1, y+2))
                avg = total // 3
                heat[y][x] = max(0, avg - random.randint(0, 1))

        for row in heat:
            print(''.join(chars[v] for v in row))
        time.sleep(0.04)

try:
    fire()
except KeyboardInterrupt:
    print("\nFire extinguished.")
