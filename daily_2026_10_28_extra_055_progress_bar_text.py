"""Render a compact textual progress bar without terminal-control features."""


def progress_bar_text(
    current: int,
    total: int,
    width: int = 20,
    *,
    complete: str = "#",
    incomplete: str = "-",
) -> str:
    """Return a bounded bar and percentage, e.g. ``[#####-----]  50%``."""
    for name, value in (("current", current), ("total", total), ("width", width)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= current <= total:
        raise ValueError("current must be between zero and total")
    if width <= 0:
        raise ValueError("width must be positive")
    for name, glyph in (("complete", complete), ("incomplete", incomplete)):
        if not isinstance(glyph, str) or len(glyph) != 1:
            raise ValueError(f"{name} must be a single-character string")
    filled = current * width // total
    percent = current * 100 // total
    return f"[{complete * filled}{incomplete * (width - filled)}] {percent:3d}%"


if __name__ == "__main__":
    assert progress_bar_text(0, 4, 8) == "[--------]   0%"
    assert progress_bar_text(2, 4, 8) == "[####----]  50%"
    assert progress_bar_text(4, 4, 8, complete="=", incomplete=".") == "[========] 100%"
    assert progress_bar_text(1, 3, 2).startswith("[--]")
    for args in ((-1, 3), (4, 3), (0, 0), (True, 3)):
        try:
            progress_bar_text(*args)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid input accepted: {args}")
    print(progress_bar_text(3, 5, 10))
