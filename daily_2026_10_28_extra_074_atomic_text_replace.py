"""Atomically replace a UTF-8 text file using a temporary sibling."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile


def atomic_text_replace(path: str | os.PathLike[str], text: str) -> None:
    """Write *text* as UTF-8, then atomically replace *path*.

    The destination's parent must already exist. A failed write leaves the
    original destination untouched and removes the temporary file when possible.
    """
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError("path must be a string or path-like object")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    destination = Path(path)
    if not destination.name or str(destination) in ("", "."):
        raise ValueError("path must name a file")
    parent = destination.parent
    if not parent.is_dir():
        raise FileNotFoundError(f"parent directory does not exist: {parent}")

    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "note.txt"
        target.write_text("old", encoding="utf-8")
        atomic_text_replace(target, "new ☃\n")
        assert target.read_text(encoding="utf-8") == "new ☃\n"
        assert sorted(p.name for p in target.parent.iterdir()) == ["note.txt"]
        try:
            atomic_text_replace(target, 42)  # type: ignore[arg-type]
        except TypeError:
            pass
        else:
            raise AssertionError("non-text input was accepted")
        assert target.read_text(encoding="utf-8") == "new ☃\n"
    print("Atomic text replacement self-check passed")
