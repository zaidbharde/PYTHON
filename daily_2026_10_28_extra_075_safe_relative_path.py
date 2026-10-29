"""Resolve untrusted relative paths while keeping them inside a chosen root."""
from __future__ import annotations

from pathlib import Path, PureWindowsPath
import os


def safe_relative_path(root: str | os.PathLike[str], candidate: str | os.PathLike[str]) -> Path:
    """Return candidate's resolved path under root; reject absolute or escaping paths.

    Backslashes are treated as separators for portable traversal checks. Existing
    symlinks are resolved too, so a symlink inside root cannot lead outside it.
    """
    if not isinstance(root, (str, os.PathLike)) or not isinstance(candidate, (str, os.PathLike)):
        raise TypeError("root and candidate must be strings or path-like objects")
    raw = os.fspath(candidate)
    if not isinstance(raw, str):
        raise TypeError("candidate must resolve to a string path")
    if not raw or "\0" in raw:
        raise ValueError("candidate must be a non-empty path without NUL bytes")
    portable = raw.replace("\\", "/")
    if Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute() or PureWindowsPath(raw).drive:
        raise ValueError("absolute paths are not allowed")
    base = Path(root).resolve()
    target = (base / portable).resolve()
    try:
        target.relative_to(base)
    except ValueError as error:
        raise ValueError("candidate escapes the chosen root") from error
    return target


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assert safe_relative_path(root, "docs/../notes.txt") == root / "notes.txt"
        for unsafe in ("../outside", "/etc/passwd", r"..\outside", "C:\\outside"):
            try:
                safe_relative_path(root, unsafe)
            except ValueError:
                pass
            else:
                raise AssertionError(f"unsafe path accepted: {unsafe!r}")
        try:
            safe_relative_path(root, "")
        except ValueError:
            pass
        else:
            raise AssertionError("empty path accepted")
    print("Safe relative path checks passed")
