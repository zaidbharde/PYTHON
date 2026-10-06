"""Create stable URL slugs without external dependencies."""

from __future__ import annotations

import re
import unicodedata


_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(value: str, *, max_length: int = 80) -> str:
    """Convert human text into a lowercase, hyphen-separated identifier.

    Accented characters are transliterated, repeated separators collapse, and
    the result is trimmed without leaving a trailing hyphen.
    """
    if max_length < 1:
        raise ValueError("max_length must be at least one")
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = _NON_WORD.sub("-", ascii_text.lower()).strip("-")
    return slug[:max_length].rstrip("-")


def unique_slug(value: str, used: set[str], *, max_length: int = 80) -> str:
    """Return a slug that is not already present in ``used``."""
    base = slugify(value, max_length=max_length) or "item"
    candidate = base
    suffix = 2
    while candidate in used:
        suffix_text = f"-{suffix}"
        candidate = f"{base[: max_length - len(suffix_text)].rstrip('-')}{suffix_text}"
        suffix += 1
    used.add(candidate)
    return candidate
