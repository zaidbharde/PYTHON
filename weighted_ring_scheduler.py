"""Deterministic weighted round-robin scheduling for named workers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Worker:
    name: str
    weight: int
    current: int = 0


class WeightedRing:
    def __init__(self, workers: Iterable[tuple[str, int]]) -> None:
        self._workers = [Worker(name, weight) for name, weight in workers]
        if not self._workers or any(worker.weight <= 0 for worker in self._workers):
            raise ValueError("workers must have positive weights")
        self._total = sum(worker.weight for worker in self._workers)

    def choose(self) -> str:
        """Return the next worker while preserving smooth weight distribution."""
        for worker in self._workers:
            worker.current += worker.weight
        selected = max(self._workers, key=lambda worker: worker.current)
        selected.current -= self._total
        return selected.name

    def schedule(self, count: int) -> list[str]:
        if count < 0:
            raise ValueError("count cannot be negative")
        return [self.choose() for _ in range(count)]

    def snapshot(self) -> dict[str, int]:
        return {worker.name: worker.current for worker in self._workers}


if __name__ == "__main__":
    router = WeightedRing([("api-a", 5), ("api-b", 3), ("api-c", 2)])
    print(" ".join(router.schedule(10)))
