import math
import time
import os
import sys

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __add__(self, o):  return Vec2(self.x+o.x, self.y+o.y)
    def __sub__(self, o):  return Vec2(self.x-o.x, self.y-o.y)
    def __mul__(self, s):  return Vec2(self.x*s, self.y*s)
    def length(self):      return (self.x**2 + self.y**2) ** 0.5
    def normalize(self):
        l = self.length()
        return Vec2(self.x/l, self.y/l) if l > 0 else Vec2()

class Particle:
    def __init__(self, x, y, vx=0, vy=0, mass=1.0, radius=1.0, char='●', color=37):
        self.pos      = Vec2(x, y)
        self.vel      = Vec2(vx, vy)
        self.acc      = Vec2()
        self.mass     = mass
        self.radius   = radius
        self.char     = char
        self.color    = color
        self.trail    = []
        self.alive    = True

class PhysicsWorld:
    def __init__(self, width=80, height=30, gravity=9.8, dt=0.05):
        self.width     = width
        self.height    = height
        self.gravity   = gravity
        self.dt        = dt
        self.particles = []
        self.walls     = True
        self.damping   = 0.98
        self.frame     = 0

    def add(self, p):
        self.particles.append(p)
        return p

    def apply_gravity(self):
        for p in self.particles:
            p.acc = Vec2(0, self.gravity)

    def apply_mutual_gravity(self, strength=500):
        for i, a in enumerate(self.particles):
            for b in self.particles[i+1:]:
                diff = b.pos - a.pos
                dist = max(diff.length(), 1.0)
                force = strength * a.mass * b.mass / (dist * dist)
                direction = diff.normalize()
                a.acc = a.acc + direction * (force / a.mass)
                b.acc = b.acc - direction * (force / b.mass)

    def update(self):
        for p in self.particles:
            if not p.alive:
                continue

            p.vel = p.vel + p.acc * self.dt
            p.vel = p.vel * self.damping
            p.pos = p.pos + p.vel * self.dt

            p.trail.append((int(p.pos.x), int(p.pos.y)))
            if len(p.trail) > 15:
                p.trail.pop(0)

            if self.walls:
                if p.pos.x <= 0 or p.pos.x >= self.width - 1:
                    p.vel.x *= -0.8
                    p.pos.x = max(0, min(self.width - 1, p.pos.x))
                if p.pos.y <= 0 or p.pos.y >= self.height - 1:
                    p.vel.y *= -0.8
                    p.pos.y = max(0, min(self.height - 1, p.pos.y))

        self.check_collisions()
        self.frame += 1

    def check_collisions(self):
        for i, a in enumerate(self.particles):
            for b in self.particles[i+1:]:
                diff = b.pos - a.pos
                dist = diff.length()
                min_dist = a.radius + b.radius

                if dist < min_dist and dist > 0:
                    normal = diff.normalize()
                    rel_vel = a.vel - b.vel
                    vel_along = rel_vel.x * normal.x + rel_vel.y * normal.y

                    if vel_along > 0:
                        restitution = 0.9
                        j = -(1 + restitution) * vel_along / (1/a.mass + 1/b.mass)
                        impulse = normal * j
                        a.vel = a.vel + impulse * (1/a.mass)
                        b.vel = b.vel - impulse * (1/b.mass)

                    overlap = min_dist - dist
                    correction = normal * (overlap / 2)
                    a.pos = a.pos - correction
                    b.pos = b.pos + correction

    def render(self):
        grid = [[' '] * self.width for _ in range(self.height)]

        for p in self.particles:
            for i, (tx, ty) in enumerate(p.trail):
                if 0 <= tx < self.width and 0 <= ty < self.height:
                    trail_chars = '·∙•'
                    idx = min(i * len(trail_chars) // len(p.trail), len(trail_chars) - 1)
                    grid[ty][tx] = trail_chars[idx]

        for p in self.particles:
            px, py = int(p.pos.x), int(p.pos.y)
            if 0 <= px < self.width and 0 <= py < self.height:
                grid[py][px] = f"\033[{p.color}m{p.char}\033[0m"

        top = '┌' + '─' * self.width + '┐'
        bot = '└' + '─' * self.width + '┘'
        lines = [top]
        for row in grid:
            lines.append('│' + ''.join(row) + '│')
        lines.append(bot)
        lines.append(f"  Frame: {self.frame} | Particles: {len(self.particles)}")

        energies = []
        for p in self.particles:
            ke = 0.5 * p.mass * p.vel.length()**2
            pe = p.mass * self.gravity * (self.height - p.pos.y)
            energies.append((ke, pe))
        total_ke = sum(ke for ke, _ in energies)
        total_pe = sum(pe for _, pe in energies)
        lines.append(f"  KE: {total_ke:.1f} | PE: {total_pe:.1f} | Total: {total_ke+total_pe:.1f}")

        return '\n'.join(lines)


def demo_bouncing():
    world = PhysicsWorld(width=60, height=20, gravity=15)
    colors = [91, 92, 93, 94, 95, 96]
    chars = '●◆■▲★◎'

    for i in range(6):
        world.add(Particle(
            x=10 + i * 8, y=2,
            vx=(i - 3) * 5, vy=0,
            mass=1 + i * 0.5,
            radius=1,
            char=chars[i],
            color=colors[i]
        ))
    return world

def demo_orbits():
    world = PhysicsWorld(width=60, height=25, gravity=0)
    world.walls = False
    world.damping = 1.0

    world.add(Particle(30, 12, 0, 0, mass=100, radius=2, char='☀', color=93))
    world.add(Particle(30, 4, 12, 0, mass=1, radius=1, char='●', color=94))
    world.add(Particle(30, 20, -10, 0, mass=1, radius=1, char='◆', color=91))
    world.add(Particle(45, 12, 0, 8, mass=0.5, radius=1, char='■', color=92))
    return world


if __name__ == "__main__":
    demos = {
        'bounce': ('Bouncing Particles', demo_bouncing),
        'orbit':  ('Orbital Mechanics', demo_orbits),
    }

    mode = sys.argv[1] if len(sys.argv) > 1 else 'bounce'
    if mode not in demos:
        mode = 'bounce'

    title, setup_fn = demos[mode]
    world = setup_fn()

    print(f"\033[2J\033[H")
    print(f"  🔬 Physics Simulation: {title}")
    print(f"  Press Ctrl+C to stop\n")
    time.sleep(1)

    try:
        for _ in range(500):
            world.apply_gravity()
            if mode == 'orbit':
                world.apply_mutual_gravity(strength=800)
            world.update()

            sys.stdout.write(f"\033[H")
            sys.stdout.write(world.render())
            sys.stdout.write('\n')
            sys.stdout.flush()
            time.sleep(0.04)
    except KeyboardInterrupt:
        print("\n  Simulation stopped.")
