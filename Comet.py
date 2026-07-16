import os, time, random

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def comet():
    w, h = 60, 20
    trail = []

    while True:
        clear()
        head_x = (int(time.time() * 10) % (w + 10)) - 10
        trail.insert(0, head_x)

        if len(trail) > 12:
            trail.pop()

        for y in range(h):
            row = [' ' for _ in range(w)]
            for i, x in enumerate(trail):
                if 0 <= x < w:
                    row[x] = '*' if i == 0 else '.' if i < 5 else '-'
            print(''.join(row))
        time.sleep(0.05)

try:
    comet()
except KeyboardInterrupt:
    print("\nComet vanished.")
