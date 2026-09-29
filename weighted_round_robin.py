"""Deterministic weighted round-robin selection for named workers."""

from collections.abc import Iterable


def weighted_round_robin(
    workers: Iterable[tuple[str, int]], cycles: int
) -> list[str]:
    """Return a fair schedule whose repetitions match each positive weight."""
    if cycles < 0:
        raise ValueError("cycles must be non-negative")
    entries = [(name, weight) for name, weight in workers if weight > 0]
    if not entries:
        return []

    schedule: list[str] = []
    current = [0] * len(entries)
    total = sum(weight for _, weight in entries)
    for _ in range(cycles):
        for index, (_, weight) in enumerate(entries):
            current[index] += weight
        winner = max(range(len(entries)), key=lambda index: current[index])
        name, _ = entries[winner]
        schedule.append(name)
        current[winner] -= total
    return schedule


if __name__ == "__main__":
    print(weighted_round_robin([("api", 3), ("worker", 1)], 8))
