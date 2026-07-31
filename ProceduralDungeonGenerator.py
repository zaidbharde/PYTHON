import random

W, H = 71, 31
grid = [["#"] * W for _ in range(H)]
rooms = []

def carve_room(x, y, w, h):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            grid[yy][xx] = " "

def carve_h(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        grid[y][x] = " "

def carve_v(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        grid[y][x] = " "

def overlaps(x, y, w, h):
    for rx, ry, rw, rh in rooms:
        if x < rx + rw + 2 and x + w + 2 > rx and y < ry + rh + 2 and y + h + 2 > ry:
            return True
    return False

for _ in range(18):
    rw = random.randint(5, 11)
    rh = random.randint(4, 8)
    x = random.randint(1, W - rw - 2)
    y = random.randint(1, H - rh - 2)

    if overlaps(x, y, rw, rh):
        continue

    carve_room(x, y, rw, rh)

    if rooms:
        px, py, pw, ph = rooms[-1]
        cx1, cy1 = x + rw // 2, y + rh // 2
        cx2, cy2 = px + pw // 2, py + ph // 2

        if random.random() < 0.5:
            carve_h(cx1, cx2, cy1)
            carve_v(cy1, cy2, cx2)
        else:
            carve_v(cy1, cy2, cx1)
            carve_h(cx1, cx2, cy2)

    rooms.append((x, y, rw, rh))

if len(rooms) >= 2:
    sx, sy, sw, sh = rooms[0]
    ex, ey, ew, eh = rooms[-1]

    start = (sx + sw // 2, sy + sh // 2)
    end = (ex + ew // 2, ey + eh // 2)

    grid[start[1]][start[0]] = "S"
    grid[end[1]][end[0]] = "E"

    for _ in range(12):
        rx, ry, rw, rh = random.choice(rooms)
        mx = random.randint(rx, rx + rw - 1)
        my = random.randint(ry, ry + rh - 1)
        if grid[my][mx] == " ":
            grid[my][mx] = random.choice(["T", "M", "C"])  # Treasure, Monster, Chest

print("=== PROCEDURAL DUNGEON ===")
print("S = Start, E = Exit, T = Treasure, M = Monster, C = Chest\n")
for row in grid:
    print("".join(row))
