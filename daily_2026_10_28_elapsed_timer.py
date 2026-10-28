"""Tiny context manager for measuring elapsed wall-clock time."""
from time import perf_counter
class ElapsedTimer:
    def __enter__(self) -> "ElapsedTimer":
        self.started = perf_counter()
        self.elapsed = 0.0
        return self
    def __exit__(self, *_: object) -> None:
        self.elapsed = perf_counter() - self.started
if __name__ == "__main__":
    with ElapsedTimer() as timer:
        sum(range(1000))
    assert timer.elapsed >= 0
    print(f"elapsed: {timer.elapsed:.6f}s")
