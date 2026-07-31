import math

class Chart:
    def __init__(self, width=60, height=15):
        self.width  = width
        self.height = height

    def bar(self, data, title="Bar Chart"):
        if not data:
            return
        labels, values = zip(*data)
        max_val = max(values)
        max_label = max(len(str(l)) for l in labels)

        print(f"\n  {title}")
        print(f"  {'─' * (self.width + max_label + 15)}")

        for label, val in data:
            bar_len = int(val / max_val * self.width) if max_val > 0 else 0
            bar = "█" * bar_len
            print(f"  {str(label):>{max_label}} │ {bar} {val}")

        print(f"  {' ' * max_label} └{'─' * (self.width + 5)}")

    def horizontal_bar(self, data, title="Comparison"):
        if not data:
            return
        labels, values = zip(*data)
        max_val = max(abs(v) for v in values)
        half = self.width // 2

        print(f"\n  {title}")
        for label, val in data:
            bar_len = int(abs(val) / max_val * half) if max_val > 0 else 0
            if val >= 0:
                bar = " " * half + "│" + "█" * bar_len
            else:
                bar = " " * (half - bar_len) + "█" * bar_len + "│"
            print(f"  {str(label):>10} {bar} {val:+}")

    def line(self, values, title="Line Chart"):
        if not values:
            return
        min_v = min(values)
        max_v = max(values)
        span = max_v - min_v if max_v != min_v else 1

        grid = [[" "] * len(values) for _ in range(self.height)]

        for x, val in enumerate(values):
            y = self.height - 1 - int((val - min_v) / span * (self.height - 1))
            grid[y][x] = "●"

            if x > 0:
                prev_y = self.height - 1 - int((values[x-1] - min_v) / span * (self.height - 1))
                step = 1 if y > prev_y else -1
                for fill_y in range(prev_y + step, y, step):
                    if 0 <= fill_y < self.height:
                        grid[fill_y][x] = "│"

        print(f"\n  {title}")
        for i, row in enumerate(grid):
            val = max_v - (i / (self.height - 1)) * span
            print(f"  {val:>7.1f} │ {''.join(row)}")
        print(f"  {'':>7} └{'─' * len(values)}")

    def scatter(self, points, title="Scatter Plot"):
        if not points:
            return
        xs, ys = zip(*points)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max_x - min_x if max_x != min_x else 1
        span_y = max_y - min_y if max_y != min_y else 1

        grid = [[" "] * self.width for _ in range(self.height)]

        for x, y in points:
            col = int((x - min_x) / span_x * (self.width - 1))
            row = self.height - 1 - int((y - min_y) / span_y * (self.height - 1))
            grid[row][col] = "●"

        print(f"\n  {title}")
        for i, row in enumerate(grid):
            val = max_y - (i / (self.height - 1)) * span_y
            print(f"  {val:>7.1f} │ {''.join(row)}")
        print(f"  {'':>7} └{'─' * self.width}")

    def pie(self, data, title="Pie Chart"):
        total = sum(v for _, v in data)
        print(f"\n  {title} (total: {total})")
        print(f"  {'─' * 40}")
        symbols = "█▓▒░◆◇○●■□"
        for i, (label, val) in enumerate(data):
            pct = val / total * 100
            bar_len = int(pct / 100 * 30)
            sym = symbols[i % len(symbols)]
            print(f"  {sym} {label:>12} : {sym * bar_len} {val} ({pct:.1f}%)")


if __name__ == "__main__":
    chart = Chart(width=50, height=12)

    print("=" * 60)
    print("  ASCII Chart Library")
    print("=" * 60)

    chart.bar([
        ("Python",     85), ("Java",       72), ("Rust",       65),
        ("Go",         58), ("JavaScript", 90), ("TypeScript", 68),
    ], title="Language Popularity")

    chart.line(
        [math.sin(x * 0.3) * 10 + 10 for x in range(50)],
        title="Sine Wave"
    )

    chart.scatter(
        [(math.cos(t * 0.2) * 10, math.sin(t * 0.3) * 8) for t in range(80)],
        title="Lissajous Pattern"
    )

    chart.horizontal_bar([
        ("Revenue", 120), ("Costs", -85), ("Profit", 35),
        ("Tax", -12), ("Net", 23),
    ], title="Financials")

    chart.pie([
        ("Chrome", 65), ("Firefox", 12), ("Safari", 15),
        ("Edge", 5), ("Other", 3),
    ], title="Browser Market Share")
