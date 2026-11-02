"""Extract ZIP files while rejecting traversal paths and symbolic-link entries.

This protects extraction paths; it does not impose a zip-bomb size limit.
"""

import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def safe_extract_zip(archive, destination):
    """Extract regular files and directories below *destination*.

    All archive members are checked before extraction starts, so an unsafe later
    member cannot leave earlier safe members partially extracted. Returns the
    paths of extracted files. Raises ``ValueError`` for unsafe member names,
    duplicate destinations, or symbolic links.
    """
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive) as source:
        checked = []
        seen = set()
        for info in source.infolist():
            name = info.filename
            posix = PurePosixPath(name)
            windows = PureWindowsPath(name)
            if (
                not name
                or "\x00" in name
                or "\\" in name
                or ":" in name
                or posix.is_absolute()
                or windows.is_absolute()
                or windows.drive
                or ".." in posix.parts
                or not posix.parts
            ):
                raise ValueError(f"unsafe ZIP member path: {name!r}")

            candidate = root.joinpath(*posix.parts)
            if candidate.is_symlink():
                raise ValueError(f"ZIP member targets a symbolic link: {name!r}")
            target = candidate.resolve()
            try:
                target.relative_to(root)
            except ValueError as error:
                raise ValueError(f"ZIP member escapes destination: {name!r}") from error

            mode = (info.external_attr >> 16) & 0o170000
            if stat.S_ISLNK(mode):
                raise ValueError(f"symbolic links are not extracted: {name!r}")
            if target in seen:
                raise ValueError(f"duplicate ZIP destination: {name!r}")
            seen.add(target)
            checked.append((info, target))

        extracted = []
        for info, target in checked:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open(info) as input_file, target.open("wb") as output_file:
                shutil.copyfileobj(input_file, output_file)
            extracted.append(target)
        return extracted
