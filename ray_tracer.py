import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
from PIL import Image

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o):      return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o):      return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s):      return Vec3(self.x*s, self.y*s, self.z*s)
    def __rmul__(self, s):     return self.__mul__(s)
    def __neg__(self):         return Vec3(-self.x, -self.y, -self.z)
    def dot(self, o):          return self.x*o.x + self.y*o.y + self.z*o.z
    def cross(self, o):        return Vec3(self.y*o.z-self.z*o.y, self.z*o.x-self.x*o.z, self.x*o.y-self.y*o.x)
    def length(self):          return (self.dot(self)) ** 0.5
    def normalize(self):       l = self.length(); return Vec3(self.x/l, self.y/l, self.z/l) if l > 0 else Vec3()
    def hadamard(self, o):     return Vec3(self.x*o.x, self.y*o.y, self.z*o.z)
    def clamp(self, lo=0, hi=1): return Vec3(max(lo,min(hi,self.x)), max(lo,min(hi,self.y)), max(lo,min(hi,self.z)))
    def to_rgb(self):          c = self.clamp(); return (int(c.x*255), int(c.y*255), int(c.z*255))

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3
    def at(self, t): return self.origin + self.direction * t

@dataclass
class Material:
    color:      Vec3
    ambient:    float = 0.1
    diffuse:    float = 0.7
    specular:   float = 0.5
    shininess:  float = 50.0
    reflective: float = 0.0

@dataclass
class HitRecord:
    point:    Vec3
    normal:   Vec3
    t:        float
    material: Material

@dataclass
class Sphere:
    center:   Vec3
    radius:   float
    material: Material

    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a  = ray.direction.dot(ray.direction)
        b  = 2.0 * oc.dot(ray.direction)
        c  = oc.dot(oc) - self.radius * self.radius
        d  = b*b - 4*a*c
        if d < 0: return None
        t = (-b - d**0.5) / (2*a)
        if t < t_min or t > t_max:
            t = (-b + d**0.5) / (2*a)
            if t < t_min or t > t_max: return None
        point  = ray.at(t)
        normal = (point - self.center).normalize()
        return HitRecord(point, normal, t, self.material)

@dataclass
class Plane:
    point:    Vec3
    normal_v: Vec3
    material: Material

    def hit(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        n = self.normal_v.normalize()
        denom = n.dot(ray.direction)
        if abs(denom) < 1e-8: return None
        t = (self.point - ray.origin).dot(n) / denom
        if t < t_min or t > t_max: return None
        point = ray.at(t)
        ix = int(abs(point.x) * 2) % 2
        iz = int(abs(point.z) * 2) % 2
        checker = self.material if (ix + iz) % 2 == 0 else Material(
            color=self.material.color * 0.3,
            ambient=self.material.ambient,
            diffuse=self.material.diffuse,
            specular=self.material.specular,
            reflective=self.material.reflective
        )
        return HitRecord(point, n, t, checker)

@dataclass
class Light:
    position:  Vec3
    color:     Vec3
    intensity: float = 1.0

class Scene:
    def __init__(self):
        self.objects: List = []
        self.lights:  List[Light] = []
        self.bg_color = Vec3(0.1, 0.1, 0.2)
        self.max_depth = 5

    def add(self, obj):    self.objects.append(obj)
    def add_light(self, l): self.lights.append(l)

    def closest_hit(self, ray, t_min=0.001, t_max=1e10) -> Optional[HitRecord]:
        closest = None
        for obj in self.objects:
            rec = obj.hit(ray, t_min, t_max)
            if rec and (closest is None or rec.t < closest.t):
                closest = rec
                t_max   = rec.t
        return closest

    def is_shadowed(self, point, light_pos):
        direction = (light_pos - point)
        dist      = direction.length()
        ray       = Ray(point, direction.normalize())
        hit       = self.closest_hit(ray, 0.001, dist)
        return hit is not None

    def shade(self, ray, rec: HitRecord, depth: int) -> Vec3:
        mat   = rec.material
        color = mat.color * mat.ambient

        for light in self.lights:
            if self.is_shadowed(rec.point, light.position): continue
            l_dir  = (light.position - rec.point).normalize()
            diff   = max(0, rec.normal.dot(l_dir))
            color  = color + mat.color.hadamard(light.color) * (diff * mat.diffuse * light.intensity)
            r_dir  = (rec.normal * (2 * rec.normal.dot(l_dir)) - l_dir).normalize()
            spec   = max(0, (-ray.direction).normalize().dot(r_dir)) ** mat.shininess
            color  = color + light.color * (spec * mat.specular * light.intensity)

        if mat.reflective > 0 and depth < self.max_depth:
            reflect_dir = ray.direction - rec.normal * (2 * ray.direction.dot(rec.normal))
            reflect_ray = Ray(rec.point, reflect_dir.normalize())
            reflect_color = self.trace(reflect_ray, depth + 1)
            color = color * (1 - mat.reflective) + reflect_color * mat.reflective

        return color

    def trace(self, ray: Ray, depth: int = 0) -> Vec3:
        rec = self.closest_hit(ray)
        if rec is None: return self.bg_color
        return self.shade(ray, rec, depth)

class Camera:
    def __init__(self, position, look_at, fov=60, width=800, height=600):
        self.position = position
        self.width    = width
        self.height   = height
        self.aspect   = width / height
        self.fov_rad  = fov * 3.14159265 / 180.0

        forward = (look_at - position).normalize()
        right   = forward.cross(Vec3(0, 1, 0)).normalize()
        up      = right.cross(forward)

        self.forward = forward
        self.right   = right
        self.up      = up

    def get_ray(self, px, py) -> Ray:
        scale = (self.fov_rad / 2.0).__class__(self.fov_rad / 2.0)
        import math
        scale = math.tan(self.fov_rad / 2.0)
        x = (2 * (px + 0.5) / self.width - 1) * self.aspect * scale
        y = (1 - 2 * (py + 0.5) / self.height) * scale
        direction = (self.forward + self.right * x + self.up * y).normalize()
        return Ray(self.position, direction)

def build_scene() -> Tuple[Scene, Camera]:
    scene = Scene()

    scene.add(Sphere(Vec3(-2, 1, -5), 1.0, Material(Vec3(1,0.2,0.2), reflective=0.3)))
    scene.add(Sphere(Vec3(0, 0.5, -3), 0.5, Material(Vec3(0.2,1,0.2), reflective=0.1)))
    scene.add(Sphere(Vec3(2, 1, -6), 1.0, Material(Vec3(0.2,0.2,1), reflective=0.5)))
    scene.add(Sphere(Vec3(0.5, 0.3, -2), 0.3, Material(Vec3(1,1,0.2), specular=0.9, shininess=100)))
    scene.add(Sphere(Vec3(-1, 2.5, -7), 1.5, Material(Vec3(0.9,0.9,0.9), reflective=0.8, specular=0.9)))
    scene.add(Plane(Vec3(0, 0, 0), Vec3(0, 1, 0), Material(Vec3(0.8,0.8,0.8), reflective=0.2)))

    scene.add_light(Light(Vec3(-5, 10, -2), Vec3(1, 1, 1), 1.0))
    scene.add_light(Light(Vec3(5, 8, -4),   Vec3(0.8, 0.8, 1), 0.6))
    scene.add_light(Light(Vec3(0, 5, 0),    Vec3(1, 0.9, 0.8), 0.3))

    camera = Camera(Vec3(0, 3, 2), Vec3(0, 1, -4), fov=60, width=800, height=600)
    return scene, camera

def render(scene, camera):
    img = Image.new('RGB', (camera.width, camera.height))
    pixels = img.load()
    total = camera.height

    for y in range(camera.height):
        if y % 50 == 0: print(f"  Rendering: {y}/{total} rows")
        for x in range(camera.width):
            ray = camera.get_ray(x, y)
            color = scene.trace(ray)
            pixels[x, y] = color.to_rgb()

    return img

if __name__ == "__main__":
    scene, camera = build_scene()
    print("Ray Tracer")
    print("=" * 40)
    img = render(scene, camera)
    img.save("render.png")
    print(f"Saved: render.png ({camera.width}x{camera.height})")
