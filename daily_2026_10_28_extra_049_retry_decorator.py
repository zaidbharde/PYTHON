"""Retry decorated calls with capped exponential delays and injectable sleep."""
from collections.abc import Callable
from functools import wraps
from math import isfinite
from time import sleep
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class RetryDecorator:
    """Retry exceptions up to ``retries`` times, sleeping between attempts."""

    def __init__(self, retries: int = 3, initial_delay: float = 0.1,
                 multiplier: float = 2.0, maximum_delay: float = 5.0,
                 sleep_fn: Callable[[float], object] = sleep) -> None:
        if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
            raise ValueError("retries must be a non-negative integer")
        if (not all(isfinite(x) for x in (initial_delay, multiplier, maximum_delay))
                or initial_delay < 0 or maximum_delay < 0 or multiplier < 1):
            raise ValueError("delays must be finite/non-negative and multiplier at least one")
        if initial_delay > maximum_delay:
            raise ValueError("maximum_delay must be at least initial_delay")
        if not callable(sleep_fn):
            raise TypeError("sleep_fn must be callable")
        self.retries, self.initial_delay = retries, initial_delay
        self.multiplier, self.maximum_delay = multiplier, maximum_delay
        self.sleep_fn = sleep_fn

    def __call__(self, function: Callable[P, R]) -> Callable[P, R]:
        if not callable(function):
            raise TypeError("decorated value must be callable")

        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            delay = self.initial_delay
            for attempt in range(self.retries + 1):
                try:
                    return function(*args, **kwargs)
                except Exception:
                    if attempt == self.retries:
                        raise
                    self.sleep_fn(delay)
                    delay = min(delay * self.multiplier, self.maximum_delay)
            raise AssertionError("unreachable")
        return wrapped


if __name__ == "__main__":
    waits: list[float] = []
    calls = 0

    @RetryDecorator(retries=3, initial_delay=0.25, maximum_delay=0.5,
                    sleep_fn=waits.append)
    def eventually_succeeds() -> str:
        global calls
        calls += 1
        if calls < 3:
            raise OSError("temporary failure")
        return "ok"

    assert eventually_succeeds() == "ok"
    assert calls == 3 and waits == [0.25, 0.5]
    print("retry decorator checks passed")
