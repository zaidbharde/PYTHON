"""Generate URL slugs while preserving uniqueness within a collection."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


def normalize_title(title: str) -> str:
    """Convert human text into a lowercase, ASCII-friendly slug stem."""
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", folded.lower())
    return "-".join(words) or "untitled"


def unique_slugs(titles: Iterable[str]) -> list[str]:
    """Return deterministic unique slugs, suffixing repeated stems numerically."""
    used: dict[str, int] = {}
    result: list[str] = []
    for title in titles:
        stem = normalize_title(title)
        occurrence = used.get(stem, 0) + 1
        used[stem] = occurrence
        result.append(stem if occurrence == 1 else f"{stem}-{occurrence}")
    return result


def reserve_slug(title: str, existing: Iterable[str]) -> str:
    """Find the first available slug without mutating the supplied collection."""
    stem = normalize_title(title)
    occupied = set(existing)
    if stem not in occupied:
        return stem
    suffix = 2
    while f"{stem}-{suffix}" in occupied:
        suffix += 1
    return f"{stem}-{suffix}"


if __name__ == "__main__":
    examples = ["Café Notes", "Cafe Notes", "Café Notes", ""]
    print("\n".join(unique_slugs(examples)))
