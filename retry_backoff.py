"""Generate bounded retry delays with deterministic jitter."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Backoff:
    initial: float = 0.25
    multiplier: float = 2.0
    maximum: float = 30.0
    jitter: float = 0.1

    def __post_init__(self) -> None:
        if self.initial <= 0 or self.multiplier < 1 or self.maximum < self.initial:
            raise ValueError("invalid backoff parameters")
        if not 0 <= self.jitter <= 1:
            raise ValueError("jitter must be between zero and one")

    def delays(self, attempts: int, seed: int = 0) -> list[float]:
        if attempts < 0:
            raise ValueError("attempts cannot be negative")
        values: list[float] = []
        state = seed & 0x7FFFFFFF
        for attempt in range(attempts):
            base = min(self.maximum, self.initial * self.multiplier ** attempt)
            state = (1103515245 * state + 12345) & 0x7FFFFFFF
            fraction = state / 0x7FFFFFFF
            factor = 1 - self.jitter + 2 * self.jitter * fraction
            values.append(min(self.maximum, round(base * factor, 6)))
        return values


def should_retry(status: int, retryable: set[int] = {408, 425, 429, 500, 502, 503, 504}) -> bool:
    """Return whether an HTTP response normally merits another attempt."""
    return status in retryable
