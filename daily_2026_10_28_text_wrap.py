"""Wrap plain text to a target width without splitting words."""
from textwrap import wrap
def wrap_text(text: str, width: int) -> list[str]:
    """Return wrapped non-empty lines; reject impossible widths."""
    if width < 1:
        raise ValueError("width must be positive")
    return wrap(" ".join(text.split()), width=width) if text.strip() else []
if __name__ == "__main__":
    lines = wrap_text("one two three", 7)
    assert lines == ["one two", "three"]
    assert all(len(line) <= 7 for line in lines)
    print("text wrapping checks passed")
