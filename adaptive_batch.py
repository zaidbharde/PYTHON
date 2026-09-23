"""Adjust a batch size using observed processing latency."""
from dataclasses import dataclass


@dataclass
class AdaptiveBatch:
    minimum: int = 1
    maximum: int = 1024
    target_seconds: float = 0.25
    size: int = 16

    def __post_init__(self) -> None:
        if not 0 < self.minimum <= self.maximum:
            raise ValueError("invalid batch bounds")
        if self.target_seconds <= 0:
            raise ValueError("target must be positive")
        self.size = min(self.maximum, max(self.minimum, self.size))

    def observe(self, elapsed_seconds: float, completed: int) -> int:
        if elapsed_seconds <= 0 or completed < 0:
            raise ValueError("observation values must be valid")
        if elapsed_seconds > self.target_seconds * 1.5:
            self.size = max(self.minimum, self.size // 2)
        elif elapsed_seconds < self.target_seconds * 0.5 and completed >= self.size:
            self.size = min(self.maximum, self.size * 2)
        return self.size

    def split(self, items: list[object]) -> list[list[object]]:
        return [items[start:start + self.size] for start in range(0, len(items), self.size)]
