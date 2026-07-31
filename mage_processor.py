import struct
import math
from dataclasses import dataclass
from typing import List, Tuple, Callable
from pathlib import Path

@dataclass
class Pixel:
    r: int
    g: int
    b: int

    def brightness(self) -> float:
        return (self.r + self.g + self.b) / (3.0 * 255)

    def grayscale(self) -> int:
        return int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)

    def to_tuple(self) -> Tuple[int, int, int]:
        return (max(0, min(255, self.r)), max(0, min(255, self.g)), max(0, min(255, self.b)))

class Image:
    def __init__(self, width: int, height: int, fill: Pixel = None):
        self.width  = width
        self.height = height
        self.pixels = [[fill or Pixel(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def get(self, x: int, y: int) -> Pixel:
        return self.pixels[max(0, min(y, self.height-1))][max(0, min(x, self.width-1))]

    def set(self, x: int, y: int, pixel: Pixel):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = pixel

    def copy(self) -> 'Image':
        img = Image(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                p = self.pixels[y][x]
                img.pixels[y][x] = Pixel(p.r, p.g, p.b)
        return img

    def apply(self, fn: Callable[[Pixel], Pixel]) -> 'Image':
        result = Image(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                result.pixels[y][x] = fn(self.pixels[y][x])
        return result

    def to_grayscale(self) -> 'Image':
        return self.apply(lambda p: Pixel(p.grayscale(), p.grayscale(), p.grayscale()))

    def invert(self) -> 'Image':
        return self.apply(lambda p: Pixel(255-p.r, 255-p.g, 255-p.b))

    def brightness_adjust(self, factor: float) -> 'Image':
        def adjust(p):
            return Pixel(
                max(0, min(255, int(p.r * factor))),
                max(0, min(255, int(p.g * factor))),
                max(0, min(255, int(p.b * factor)))
            )
        return self.apply(adjust)

    def contrast(self, factor: float) -> 'Image':
        def adjust(p):
            return Pixel(
                max(0, min(255, int(128 + (p.r - 128) * factor))),
                max(0, min(255, int(128 + (p.g - 128) * factor))),
                max(0, min(255, int(128 + (p.b - 128) * factor)))
            )
        return self.apply(adjust)

    def sepia(self) -> 'Image':
        def apply_sepia(p):
            tr = int(min(255, p.r * 0.393 + p.g * 0.769 + p.b * 0.189))
            tg = int(min(255, p.r * 0.349 + p.g * 0.686 + p.b * 0.168))
            tb = int(min(255, p.r * 0.272 + p.g * 0.534 + p.b * 0.131))
            return Pixel(tr, tg, tb)
        return self.apply(apply_sepia)

    def threshold(self, level: int = 128) -> 'Image':
        def thresh(p):
            v = 255 if p.grayscale() >= level else 0
            return Pixel(v, v, v)
        return self.apply(thresh)

    def convolve(self, kernel: List[List[float]]) -> 'Image':
        result = Image(self.width, self.height)
        kh = len(kernel) // 2
        kw = len(kernel[0]) // 2

        for y in range(self.height):
            for x in range(self.width):
                r_sum = g_sum = b_sum = 0.0
                for ky in range(len(kernel)):
                    for kx in range(len(kernel[0])):
                        px = self.get(x + kx - kw, y + ky - kh)
                        w  = kernel[ky][kx]
                        r_sum += px.r * w
                        g_sum += px.g * w
                        b_sum += px.b * w
                result.set(x, y, Pixel(
                    max(0, min(255, int(r_sum))),
                    max(0, min(255, int(g_sum))),
                    max(0, min(255, int(b_sum)))
                ))
        return result

    def blur(self, radius: int = 1) -> 'Image':
        size = 2 * radius + 1
        val  = 1.0 / (size * size)
        kernel = [[val] * size for _ in range(size)]
        return self.convolve(kernel)

    def gaussian_blur(self, sigma: float = 1.0) -> 'Image':
        radius = int(3 * sigma)
        size   = 2 * radius + 1
        kernel = [[0.0] * size for _ in range(size)]
        total  = 0.0

        for y in range(size):
            for x in range(size):
                dx, dy = x - radius, y - radius
                kernel[y][x] = math.exp(-(dx*dx + dy*dy) / (2*sigma*sigma))
                total += kernel[y][x]

        for y in range(size):
            for x in range(size):
                kernel[y][x] /= total

        return self.convolve(kernel)

    def sharpen(self) -> 'Image':
        kernel = [[0,-1,0], [-1,5,-1], [0,-1,0]]
        return self.convolve(kernel)

    def edge_detect(self) -> 'Image':
        kernel = [[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]
        return self.convolve(kernel)

    def emboss(self) -> 'Image':
        kernel = [[-2,-1,0], [-1,1,1], [0,1,2]]
        return self.convolve(kernel)

    def flip_horizontal(self) -> 'Image':
        result = Image(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                result.pixels[y][x] = self.pixels[y][self.width - 1 - x]
        return result

    def flip_vertical(self) -> 'Image':
        result = Image(self.width, self.height)
        for y in range(self.height):
            result.pixels[y] = self.pixels[self.height - 1 - y][:]
        return result

    def rotate_90(self) -> 'Image':
        result = Image(self.height, self.width)
        for y in range(self.height):
            for x in range(self.width):
                result.pixels[x][self.height - 1 - y] = self.pixels[y][x]
        return result

    def resize(self, new_width: int, new_height: int) -> 'Image':
        result = Image(new_width, new_height)
        x_ratio = self.width / new_width
        y_ratio = self.height / new_height

        for y in range(new_height):
            for x in range(new_width):
                src_x = int(x * x_ratio)
                src_y = int(y * y_ratio)
                result.pixels[y][x] = self.get(src_x, src_y)
        return result

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> 'Image':
        w = x2 - x1
        h = y2 - y1
        result = Image(w, h)
        for y in range(h):
            for x in range(w):
                result.pixels[y][x] = self.get(x + x1, y + y1)
        return result

    def histogram(self) -> dict:
        hist = {"r": [0]*256, "g": [0]*256, "b": [0]*256, "luminance": [0]*256}
        for y in range(self.height):
            for x in range(self.width):
                p = self.pixels[y][x]
                hist["r"][p.r] += 1
                hist["g"][p.g] += 1
                hist["b"][p.b] += 1
                hist["luminance"][p.grayscale()] += 1
        return hist

    def stats(self) -> dict:
        total = self.width * self.height
        r_sum = g_sum = b_sum = 0
        r_min = g_min = b_min = 255
        r_max = g_max = b_max = 0

        for y in range(self.height):
            for x in range(self.width):
                p = self.pixels[y][x]
                r_sum += p.r; g_sum += p.g; b_sum += p.b
                r_min = min(r_min, p.r); r_max = max(r_max, p.r)
                g_min = min(g_min, p.g); g_max = max(g_max, p.g)
                b_min = min(b_min, p.b); b_max = max(b_max, p.b)

        return {
            "dimensions": f"{self.width}x{self.height}",
            "pixels": total,
            "avg_r": r_sum / total, "avg_g": g_sum / total, "avg_b": b_sum / total,
            "range_r": (r_min, r_max), "range_g": (g_min, g_max), "range_b": (b_min, b_max),
        }

    def save_ppm(self, path: str):
        with open(path, 'wb') as f:
            header = f"P6\n{self.width} {self.height}\n255\n".encode()
            f.write(header)
            for y in range(self.height):
                for x in range(self.width):
                    p = self.pixels[y][x].to_tuple()
                    f.write(struct.pack('BBB', *p))

    @staticmethod
    def load_ppm(path: str) -> 'Image':
        with open(path, 'rb') as f:
            magic = f.readline().strip()
            line  = f.readline().strip()
            while line.startswith(b'#'): line = f.readline().strip()
            w, h = map(int, line.split())
            maxval = int(f.readline().strip())
            img = Image(w, h)
            for y in range(h):
                for x in range(w):
                    r, g, b = struct.unpack('BBB', f.read(3))
                    img.pixels[y][x] = Pixel(r, g, b)
            return img

    def to_ascii(self, width: int = 80) -> str:
        chars  = " .:-=+*#%@"
        ratio  = width / self.width
        height = int(self.height * ratio * 0.5)
        resized = self.resize(width, height)
        gray    = resized.to_grayscale()

        lines = []
        for y in range(gray.height):
            line = ""
            for x in range(gray.width):
                brightness = gray.pixels[y][x].r / 255.0
                idx = int(brightness * (len(chars) - 1))
                line += chars[idx]
            lines.append(line)
        return "\n".join(lines)


def generate_gradient(width: int, height: int) -> Image:
    img = Image(width, height)
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(255 * (1 - x / width))
            img.set(x, y, Pixel(r, g, b))
    return img

def generate_mandelbrot(width: int, height: int, max_iter: int = 100) -> Image:
    img = Image(width, height)
    for py in range(height):
        for px in range(width):
            x0 = (px / width) * 3.5 - 2.5
            y0 = (py / height) * 2.0 - 1.0
            x, y, iteration = 0.0, 0.0, 0

            while x*x + y*y <= 4 and iteration < max_iter:
                x, y = x*x - y*y + x0, 2*x*y + y0
                iteration += 1

            if iteration == max_iter:
                img.set(px, py, Pixel(0, 0, 0))
            else:
                t = iteration / max_iter
                r = int(9 * (1-t) * t * t * t * 255)
                g = int(15 * (1-t) * (1-t) * t * t * 255)
                b = int(8.5 * (1-t) * (1-t) * (1-t) * t * 255)
                img.set(px, py, Pixel(r, g, b))
    return img


if __name__ == "__main__":
    print("=" * 50)
    print("  Image Processor")
    print("=" * 50)

    print("\n  Generating gradient image (200x150)...")
    gradient = generate_gradient(200, 150)
    gradient.save_ppm("gradient.ppm")

    stats = gradient.stats()
    print(f"  Dimensions: {stats['dimensions']}")
    print(f"  Pixels: {stats['pixels']}")
    print(f"  Avg RGB: ({stats['avg_r']:.1f}, {stats['avg_g']:.1f}, {stats['avg_b']:.1f})")

    print("\n  Applying filters...")
    filters = {
        "grayscale":  gradient.to_grayscale(),
        "inverted":   gradient.invert(),
        "sepia":      gradient.sepia(),
        "bright":     gradient.brightness_adjust(1.5),
        "contrast":   gradient.contrast(1.8),
        "threshold":  gradient.threshold(128),
        "blurred":    gradient.blur(2),
        "sharpened":  gradient.sharpen(),
        "edges":      gradient.edge_detect(),
        "embossed":   gradient.emboss(),
        "flipped_h":  gradient.flip_horizontal(),
        "flipped_v":  gradient.flip_vertical(),
        "rotated":    gradient.rotate_90(),
        "cropped":    gradient.crop(25, 25, 175, 125),
        "resized":    gradient.resize(100, 75),
    }

    for name, img in filters.items():
        filename = f"{name}.ppm"
        img.save_ppm(filename)
        print(f"    {name:<14} → {filename} ({img.width}x{img.height})")

    print("\n  Generating Mandelbrot (300x200)...")
    mandelbrot = generate_mandelbrot(300, 200, max_iter=80)
    mandelbrot.save_ppm("mandelbrot.ppm")

    print("\n  ASCII art (Mandelbrot):")
    print(mandelbrot.to_ascii(60))

    import glob
    for f in glob.glob("*.ppm"):
        Path(f).unlink()
    print("\n  Cleaned up temp files.")
