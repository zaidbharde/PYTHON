"""Summarize predicted prices into readable, comparable windows."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True)
class PriceWindow:
    """A price range with a representative midpoint."""

    minimum: float
    maximum: float
    average: float

    def __post_init__(self) -> None:
        if self.minimum < 0 or self.maximum < self.minimum:
            raise ValueError("price bounds are invalid")


def summarize_prices(prices: Iterable[float], *, quantile: float = 0.1) -> PriceWindow:
    """Return a trimmed range after discarding extreme tails."""
    values = sorted(float(price) for price in prices)
    if not values:
        raise ValueError("at least one price is required")
    if not 0 <= quantile < 0.5:
        raise ValueError("quantile must be in the half-open interval [0, 0.5)")
    trim = int(len(values) * quantile)
    kept = values[trim : len(values) - trim or None]
    return PriceWindow(minimum=kept[0], maximum=kept[-1], average=fmean(kept))


def format_window(window: PriceWindow, *, currency: str = "$") -> str:
    """Format a window for a dashboard label."""
    return f"{currency}{window.minimum:,.0f}–{currency}{window.maximum:,.0f} (avg {currency}{window.average:,.0f})"
