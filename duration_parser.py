"""Parse compact human durations such as ``1h 20m 5s`` safely."""

from __future__ import annotations

import re

_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}
_TOKEN = re.compile(r"(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>[smhd])", re.IGNORECASE)


def parse_duration(text: str) -> float:
    """Return seconds represented by *text*, rejecting gaps or duplicate units."""
    position = 0
    total = 0.0
    seen: set[str] = set()
    matches = list(_TOKEN.finditer(text))
    if not matches:
        raise ValueError("duration must contain at least one number and unit")
    for match in matches:
        gap = text[position : match.start()]
        if gap.strip():
            raise ValueError(f"unexpected text at position {position}: {gap!r}")
        unit = match.group("unit").lower()
        if unit in seen:
            raise ValueError(f"duplicate unit: {unit}")
        seen.add(unit)
        total += float(match.group("amount")) * _UNITS[unit]
        position = match.end()
    if text[position:].strip():
        raise ValueError(f"unexpected trailing text: {text[position:]!r}")
    return total


def format_duration(seconds: float) -> str:
    """Render seconds into descending whole-day/hour/minute/second components."""
    if seconds < 0:
        raise ValueError("seconds cannot be negative")
    remainder = int(seconds)
    parts: list[str] = []
    for suffix, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        amount, remainder = divmod(remainder, size)
        if amount:
            parts.append(f"{amount}{suffix}")
    return " ".join(parts) or "0s"


if __name__ == "__main__":
    sample = "1d 2h 3m 4s"
    print(sample, "=", format_duration(parse_duration(sample)))
