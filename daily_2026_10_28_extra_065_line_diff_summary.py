"""Summarize added and removed lines between two text versions."""
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class LineDiffSummary:
    """Changed-line details, retaining source/target order within each side."""

    added: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def summarize_line_diff(before: str, after: str) -> LineDiffSummary:
    """Return added and removed lines; a replacement appears in both tuples.

    Text is split into logical lines, so final newline presence does not create
    a phantom changed line. Matching is exact and case-sensitive.
    """
    if not isinstance(before, str) or not isinstance(after, str):
        raise TypeError("before and after must be strings")
    old_lines, new_lines = before.splitlines(), after.splitlines()
    added: list[str] = []
    removed: list[str] = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(
        a=old_lines, b=new_lines, autojunk=False
    ).get_opcodes():
        if tag in ("delete", "replace"):
            removed.extend(old_lines[i1:i2])
        if tag in ("insert", "replace"):
            added.extend(new_lines[j1:j2])
    return LineDiffSummary(tuple(added), tuple(removed))


if __name__ == "__main__":
    result = summarize_line_diff("keep\nold\n", "keep\nnew\nextra\n")
    assert result.added == ("new", "extra")
    assert result.removed == ("old",)
    assert (result.added_count, result.removed_count) == (2, 1)
    assert summarize_line_diff("same\n", "same").added_count == 0
    assert summarize_line_diff("", "x").added == ("x",)
    try:
        summarize_line_diff(None, "x")  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string input should be rejected")
    print("LineDiffSummary self-check passed")
