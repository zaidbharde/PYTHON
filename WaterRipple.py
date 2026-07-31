import time, os, math

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def ripple():
    w, h = 60, 30
    cx, cy = w // 2, h // 2
    chars = " .,-~:;=!*#$@"

    while True:
        clear()
        t = time.time()
        for y in range(h):
            row = ''
            for x in range(w):
                dx, dy = x - cx, y - cy
                d = math.sqrt(dx**2 + dy**2)
                v = math.sin(d - t * 5)
                row += chars[int((v + 1) / 2 * (len(chars) - 1))]
            print(row)
        time.sleep(0.07)

try:
    ripple()
except KeyboardInterrupt:
    print("\nSplash ended.")
