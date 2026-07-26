import random
import math

class PerlinNoise:
    def __init__(self, seed=42):
        random.seed(seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        return a + t * (b - a)

    def _grad(self, h, x, y):
        h = h & 3
        if h == 0: return x + y
        if h == 1: return -x + y
        if h == 2: return x - y
        return -x - y

    def noise(self, x, y):
        xi, yi = int(x) & 255, int(y) & 255
        xf, yf = x - int(x), y - int(y)
        u, v = self._fade(xf), self._fade(yf)

        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]

        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf-1, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf-1), self._grad(bb, xf-1, yf-1), u)
        return self._lerp(x1, x2, v)

    def octave_noise(self, x, y, octaves=6, persistence=0.5):
        total = 0
        amplitude = 1.0
        frequency = 1.0
        max_val = 0
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= persistence
            frequency *= 2
        return total / max_val


class TerrainGenerator:
    BIOMES = {
        'deep_water':  ('🌊', '\033[34m',  -0.3),
        'water':       ('~~', '\033[94m',  -0.1),
        'beach':       ('░░', '\033[93m',   0.0),
        'grass':       ('▒▒', '\033[32m',   0.15),
        'forest':      ('🌲', '\033[92m',   0.3),
        'mountain':    ('▓▓', '\033[37m',   0.5),
        'snow':        ('██', '\033[97m',   0.7),
    }

    def __init__(self, width=80, height=30, seed=42):
        self.width = width
        self.height = height
        self.noise = PerlinNoise(seed)
        self.moisture_noise = PerlinNoise(seed + 100)
        self.grid = [[0.0] * width for _ in range(height)]
        self.biome_grid = [[''] * width for _ in range(height)]

    def generate(self, scale=0.05, octaves=6):
        for y in range(self.height):
            for x in range(self.width):
                elevation = self.noise.octave_noise(x * scale, y * scale, octaves)

                cx = abs(x - self.width / 2) / (self.width / 2)
                cy = abs(y - self.height / 2) / (self.height / 2)
                edge = max(cx, cy)
                elevation -= edge * 0.5

                self.grid[y][x] = elevation
                self.biome_grid[y][x] = self._get_biome(elevation)

    def _get_biome(self, elevation):
        for name, (_, _, threshold) in sorted(self.BIOMES.items(), key=lambda x: x[1][2], reverse=True):
            if elevation >= threshold:
                return name
        return 'deep_water'

    def render(self, colored=True):
        reset = '\033[0m'
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                biome = self.biome_grid[y][x]
                symbol, color, _ = self.BIOMES[biome]
                if colored:
                    row.append(f"{color}{symbol}{reset}")
                else:
                    row.append(symbol)
            lines.append(''.join(row))
        return '\n'.join(lines)

    def render_heightmap(self):
        chars = ' ░▒▓█'
        lines = []
        vals = [v for row in self.grid for v in row]
        lo, hi = min(vals), max(vals)
        span = hi - lo if hi != lo else 1

        for y in range(self.height):
            row = []
            for x in range(self.width):
                normalized = (self.grid[y][x] - lo) / span
                idx = min(len(chars) - 1, int(normalized * len(chars)))
                row.append(chars[idx] * 2)
            lines.append(''.join(row))
        return '\n'.join(lines)

    def stats(self):
        counts = {}
        for row in self.biome_grid:
            for biome in row:
                counts[biome] = counts.get(biome, 0) + 1

        total = self.width * self.height
        vals = [v for row in self.grid for v in row]

        print(f"\n  Terrain Statistics:")
        print(f"  {'─' * 45}")
        print(f"  Size        : {self.width}x{self.height} ({total} tiles)")
        print(f"  Elevation   : {min(vals):.3f} to {max(vals):.3f}")
        print(f"  Mean elev   : {sum(vals)/len(vals):.3f}")

        print(f"\n  Biome Distribution:")
        for biome in sorted(counts, key=lambda b: self.BIOMES[b][2]):
            count = counts[biome]
            pct = count / total * 100
            bar = '█' * int(pct / 2)
            symbol, color, _ = self.BIOMES[biome]
            print(f"  {color}{symbol}\033[0m {biome:>12} : {count:>5} ({pct:>5.1f}%) {bar}")

    def find_path(self, start, end):
        import heapq
        open_set = [(0, start)]
        came_from = {}
        cost = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = current[0]+dx, current[1]+dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    biome = self.biome_grid[ny][nx]
                    if biome in ('deep_water', 'water'):
                        continue
                    move_cost = 1 + max(0, self.grid[ny][nx] - self.grid[current[1]][current[0]]) * 10
                    new_cost = cost[current] + move_cost
                    neighbor = (nx, ny)
                    if neighbor not in cost or new_cost < cost[neighbor]:
                        cost[neighbor] = new_cost
                        priority = new_cost + abs(nx-end[0]) + abs(ny-end[1])
                        heapq.heappush(open_set, (priority, neighbor))
                        came_from[neighbor] = current
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("  🗺️  Procedural Terrain Generator")
    print("=" * 60)

    gen = TerrainGenerator(width=50, height=22, seed=42)
    gen.generate(scale=0.06, octaves=6)

    print("\n  Colored terrain:")
    print(gen.render(colored=True))

    gen.stats()

    print(f"\n  Heightmap:")
    print(gen.render_heightmap())

    print(f"\n  Pathfinding (A*):")
    path = gen.find_path((5, 10), (45, 10))
    if path:
        print(f"  Path found: {len(path)} steps")
        print(f"  Start: {path[0]} → End: {path[-1]}")
        biomes_crossed = set(gen.biome_grid[p[1]][p[0]] for p in path)
        print(f"  Biomes crossed: {biomes_crossed}")
    else:
        print("  No path found!")
