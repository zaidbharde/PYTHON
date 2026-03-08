import pygame
import math
import random
from colorsys import hsv_to_rgb

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ Design Animation ✨")
clock = pygame.time.Clock()

# Particle class
class Particle:
    def __init__(self, x, y, hue):
        self.x = x
        self.y = y
        self.hue = hue
        self.size = random.randint(2, 6)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, math.pi * 2)
        self.life = 255
        self.decay = random.uniform(2, 5)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= self.decay
        self.hue = (self.hue + 0.5) % 360
        
    def draw(self, surface):
        if self.life > 0:
            rgb = hsv_to_rgb(self.hue / 360, 0.8, 1)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), int(self.life))
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))
            
    def is_alive(self):
        return self.life > 0

# Orbiting shape class
class OrbitingShape:
    def __init__(self, center_x, center_y, radius, speed, shape_type, hue):
        self.cx = center_x
        self.cy = center_y
        self.radius = radius
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = speed
        self.shape_type = shape_type
        self.hue = hue
        self.size = random.randint(5, 15)
        self.trail = []
        
    def update(self):
        self.angle += self.speed
        self.hue = (self.hue + 0.3) % 360
        x = self.cx + math.cos(self.angle) * self.radius
        y = self.cy + math.sin(self.angle) * self.radius
        self.trail.append((x, y, self.hue))
        if len(self.trail) > 50:
            self.trail.pop(0)
            
    def draw(self, surface):
        # Draw trail
        for i, (tx, ty, thue) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 200)
            rgb = hsv_to_rgb(thue / 360, 0.7, 1)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            size = int((i / len(self.trail)) * self.size)
            if size > 0:
                pygame.draw.circle(surface, color, (int(tx), int(ty)), size)
        
        # Draw main shape
        x = self.cx + math.cos(self.angle) * self.radius
        y = self.cy + math.sin(self.angle) * self.radius
        rgb = hsv_to_rgb(self.hue / 360, 1, 1)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        
        if self.shape_type == 0:
            pygame.draw.circle(surface, color, (int(x), int(y)), self.size)
        elif self.shape_type == 1:
            rect = pygame.Rect(int(x - self.size), int(y - self.size), self.size * 2, self.size * 2)
            pygame.draw.rect(surface, color, rect)
        else:
            points = []
            for i in range(3):
                px = x + math.cos(self.angle + i * math.pi * 2 / 3) * self.size
                py = y + math.sin(self.angle + i * math.pi * 2 / 3) * self.size
                points.append((px, py))
            pygame.draw.polygon(surface, color, points)

# Wave ring class
class WaveRing:
    def __init__(self, x, y, hue):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 200
        self.hue = hue
        self.life = 255
        
    def update(self):
        self.radius += 3
        self.life = 255 * (1 - self.radius / self.max_radius)
        
    def draw(self, surface):
        if self.life > 0 and self.radius < self.max_radius:
            rgb = hsv_to_rgb(self.hue / 360, 0.8, 1)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.radius), 3)
            
    def is_alive(self):
        return self.radius < self.max_radius

# Background pattern drawer
def draw_background_pattern(surface, time):
    surface.fill((10, 10, 20))
    
    # Draw grid of dots
    for x in range(0, WIDTH, 40):
        for y in range(0, HEIGHT, 40):
            wave = math.sin(time * 0.02 + x * 0.01 + y * 0.01)
            size = int(2 + wave * 2)
            alpha = int(50 + wave * 30)
            hue = (time + x + y) % 360
            rgb = hsv_to_rgb(hue / 360, 0.3, 0.3)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            if size > 0:
                pygame.draw.circle(surface, color, (x, y), size)

# Draw spiral
def draw_spiral(surface, cx, cy, time, hue_offset):
    points = []
    for i in range(200):
        angle = i * 0.1 + time * 0.02
        radius = i * 1.5
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        points.append((x, y))
        
        hue = (hue_offset + i * 2) % 360
        rgb = hsv_to_rgb(hue / 360, 0.8, 0.9)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        size = max(1, int(5 - i * 0.02))
        pygame.draw.circle(surface, color, (int(x), int(y)), size)
    
    if len(points) > 1:
        hue = (hue_offset + time) % 360
        rgb = hsv_to_rgb(hue / 360, 0.5, 0.7)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        pygame.draw.lines(surface, color, False, [(int(p[0]), int(p[1])) for p in points], 1)

# Draw pulsing center
def draw_pulsing_center(surface, cx, cy, time, hue):
    pulse = math.sin(time * 0.05) * 20 + 50
    for i in range(5, 0, -1):
        r = pulse + i * 15
        alpha = 150 - i * 25
        h = (hue + i * 20) % 360
        rgb = hsv_to_rgb(h / 360, 0.8, 0.9)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        pygame.draw.circle(surface, color, (int(cx), int(cy)), int(r), 3)

# Main animation variables
particles = []
orbiting_shapes = []
wave_rings = []
time = 0
center_hue = 0

# Create orbiting shapes
for i in range(8):
    radius = 80 + i * 30
    speed = 0.02 - i * 0.002
    hue = i * 45
    shape = OrbitingShape(WIDTH // 2, HEIGHT // 2, radius, speed, i % 3, hue)
    orbiting_shapes.append(shape)

# Font for text
font = pygame.font.Font(None, 36)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Create wave ring on click
            mx, my = pygame.mouse.get_pos()
            wave_rings.append(WaveRing(mx, my, center_hue))
            # Create particles
            for _ in range(20):
                particles.append(Particle(mx, my, center_hue))
    
    # Update time and hue
    time += 1
    center_hue = (center_hue + 0.5) % 360
    
    # Draw background
    draw_background_pattern(screen, time)
    
    # Draw spiral
    draw_spiral(screen, WIDTH // 2, HEIGHT // 2, time, center_hue)
    
    # Draw pulsing center
    draw_pulsing_center(screen, WIDTH // 2, HEIGHT // 2, time, center_hue)
    
    # Update and draw orbiting shapes
    for shape in orbiting_shapes:
        shape.update()
        shape.draw(screen)
    
    # Spawn particles occasionally
    if random.random() < 0.3:
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(50, 150)
        px = WIDTH // 2 + math.cos(angle) * dist
        py = HEIGHT // 2 + math.sin(angle) * dist
        particles.append(Particle(px, py, center_hue))
    
    # Update and draw particles
    particles = [p for p in particles if p.is_alive()]
    for particle in particles:
        particle.update()
        particle.draw(screen)
    
    # Update and draw wave rings
    wave_rings = [w for w in wave_rings if w.is_alive()]
    for ring in wave_rings:
        ring.update()
        ring.draw(screen)
    
    # Draw rotating polygon
    num_sides = 6
    poly_radius = 50 + math.sin(time * 0.03) * 20
    poly_points = []
    for i in range(num_sides):
        angle = time * 0.02 + i * math.pi * 2 / num_sides
        x = WIDTH // 2 + math.cos(angle) * poly_radius
        y = HEIGHT // 2 + math.sin(angle) * poly_radius
        poly_points.append((x, y))
    
    rgb = hsv_to_rgb(center_hue / 360, 0.9, 1)
    poly_color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    pygame.draw.polygon(screen, poly_color, poly_points, 3)
    
    # Draw corner decorations
    corners = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
    for i, (cx, cy) in enumerate(corners):
        for j in range(5):
            arc_radius = 30 + j * 20 + math.sin(time * 0.03 + i) * 10
            h = (center_hue + i * 30 + j * 10) % 360
            rgb = hsv_to_rgb(h / 360, 0.6, 0.8)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            start_angle = i * math.pi / 2
            rect = pygame.Rect(cx - arc_radius, cy - arc_radius, arc_radius * 2, arc_radius * 2)
            pygame.draw.arc(screen, color, rect, start_angle, start_angle + math.pi / 2, 2)
    
    # Draw info text
    text = font.render("Click anywhere to create effects!", True, (200, 200, 200))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 40))
    
    # FPS counter
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (100, 100, 100))
    screen.blit(fps_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
