"""Compare CSV-like schemas and produce actionable migration details."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SchemaDiff:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    reordered: bool

    @property
    def compatible(self) -> bool:
        """Whether old columns remain in the same order with no removals."""
        return not self.removed and not self.reordered

    def as_messages(self) -> list[str]:
        """Format the diff for a migration report."""
        messages = [f"added column: {name}" for name in self.added]
        messages.extend(f"removed column: {name}" for name in self.removed)
        if self.reordered:
            messages.append("existing columns changed order")
        return messages or ["schemas are identical"]


def compare_schema(old: Iterable[str], new: Iterable[str]) -> SchemaDiff:
    """Compare unique column sequences while rejecting duplicate names."""
    before = tuple(old)
    after = tuple(new)
    if len(set(before)) != len(before) or len(set(after)) != len(after):
        raise ValueError("schema columns must be unique")
    before_set, after_set = set(before), set(after)
    added = tuple(name for name in after if name not in before_set)
    removed = tuple(name for name in before if name not in after_set)
    common_before = tuple(name for name in before if name in after_set)
    common_after = tuple(name for name in after if name in before_set)
    return SchemaDiff(added, removed, common_before != common_after)


def require_compatible(old: Iterable[str], new: Iterable[str]) -> None:
    """Raise a clear error when a schema change needs a migration."""
    diff = compare_schema(old, new)
    if not diff.compatible:
        raise ValueError("; ".join(diff.as_messages()))


if __name__ == "__main__":
    diff = compare_schema(["id", "name"], ["id", "name", "email"])
    assert diff.compatible and diff.added == ("email",)
    assert compare_schema(["id", "name"], ["name", "id"]).reordered
    print("schema diff checks passed")
