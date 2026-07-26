import colorsys

class Color:
    def __init__(self, r, g, b):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))

    @classmethod
    def from_hex(cls, hex_str):
        h = hex_str.lstrip('#')
        return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @classmethod
    def from_hsl(cls, h, s, l):
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return cls(int(r * 255), int(g * 255), int(b * 255))

    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_hsl(self):
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return int(h * 360), int(s * 100), int(l * 100)

    def to_cmyk(self):
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        k = 1 - max(r, g, b)
        if k == 1:
            return 0, 0, 0, 100
        c = int((1 - r - k) / (1 - k) * 100)
        m = int((1 - g - k) / (1 - k) * 100)
        y = int((1 - b - k) / (1 - k) * 100)
        return c, m, y, int(k * 100)

    def luminance(self):
        def lin(v):
            v = v / 255
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(self.r) + 0.7152 * lin(self.g) + 0.0722 * lin(self.b)

    def contrast_ratio(self, other):
        l1 = max(self.luminance(), other.luminance())
        l2 = min(self.luminance(), other.luminance())
        return (l1 + 0.05) / (l2 + 0.05)

    def complement(self):
        return Color(255 - self.r, 255 - self.g, 255 - self.b)

    def lighten(self, pct=20):
        h, s, l = self.to_hsl()
        return Color.from_hsl(h, s, min(100, l + pct))

    def darken(self, pct=20):
        h, s, l = self.to_hsl()
        return Color.from_hsl(h, s, max(0, l - pct))

    def grayscale(self):
        g = int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)
        return Color(g, g, g)

    def ansi_block(self):
        return f"\033[48;2;{self.r};{self.g};{self.b}m   \033[0m"

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b})"


if __name__ == "__main__":
    colors = {
        "Red":     Color(255, 0, 0),
        "Green":   Color(0, 128, 0),
        "Blue":    Color.from_hex("#3498db"),
        "Purple":  Color.from_hex("#9b59b6"),
        "Orange":  Color.from_hex("#e67e22"),
        "Teal":    Color.from_hsl(180, 70, 40),
    }

    print("=" * 60)
    print("  Color Picker")
    print("=" * 60)

    for name, c in colors.items():
        h, s, l = c.to_hsl()
        cm, m, y, k = c.to_cmyk()
        print(f"\n  {name}: {c.ansi_block()}")
        print(f"    RGB  : ({c.r}, {c.g}, {c.b})")
        print(f"    HEX  : {c.to_hex()}")
        print(f"    HSL  : ({h}°, {s}%, {l}%)")
        print(f"    CMYK : ({cm}%, {m}%, {y}%, {k}%)")
        print(f"    Complement : {c.complement().to_hex()} {c.complement().ansi_block()}")
        print(f"    Lighter    : {c.lighten().to_hex()} {c.lighten().ansi_block()}")
        print(f"    Darker     : {c.darken().to_hex()} {c.darken().ansi_block()}")
        print(f"    Grayscale  : {c.grayscale().to_hex()} {c.grayscale().ansi_block()}")

    white = Color(255, 255, 255)
    black = Color(0, 0, 0)
    print(f"\n  Contrast Ratios (WCAG):")
    for name, c in colors.items():
        cw 
