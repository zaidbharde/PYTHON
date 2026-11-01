"""Group names that become identical under Unicode normalization and case rules."""
from __future__ import annotations

import unicodedata
from collections import defaultdict
from collections.abc import Iterable

_NORMALIZATION_FORMS = {"NFC", "NFD", "NFKC", "NFKD"}


def collision_groups(
    names: Iterable[str], *, normalization: str = "NFC", case_fold: bool = False
) -> list[list[str]]:
    """Return stable groups of original names with equal normalized keys.

    Groups and members follow first-seen input order. Only groups with at least
    two members are returned; repeated identical spellings count as collisions.
    Set ``case_fold`` to compare using Unicode's full, locale-independent fold.
    """
    if normalization not in _NORMALIZATION_FORMS:
        raise ValueError(
            f"normalization must be one of {', '.join(sorted(_NORMALIZATION_FORMS))}"
        )

    grouped: dict[str, list[str]] = defaultdict(list)
    for name in names:
        if not isinstance(name, str):
            raise TypeError("all names must be strings")
        key = unicodedata.normalize(normalization, name)
        if case_fold:
            key = unicodedata.normalize(normalization, key.casefold())
        grouped[key].append(name)
    return [members for members in grouped.values() if len(members) > 1]
