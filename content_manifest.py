"""Build and compare deterministic SHA-256 manifests for directory trees."""

from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Mapping


def _file_digest(path: Path, chunk_size: int) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    root: os.PathLike[str] | str,
    *,
    chunk_size: int = 1024 * 1024,
    follow_symlinks: bool = False,
) -> Dict[str, str]:
    """Return ``{relative_posix_path: sha256_hex}`` for regular files under root.

    Paths and output ordering are deterministic. Symlinks are skipped by default;
    with ``follow_symlinks=True`` file links are hashed and directory links are
    traversed, while visited directory inodes prevent cycles. Missing roots and
    filesystem errors are intentionally reported to the caller.
    """
    base = Path(root)
    if not base.exists():
        raise FileNotFoundError(os.fspath(base))
    if not base.is_dir():
        raise NotADirectoryError(os.fspath(base))
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    manifest: Dict[str, str] = {}
    visited_dirs = set()

    def walk(directory: Path) -> None:
        stat = directory.stat()
        identity = (stat.st_dev, stat.st_ino)
        if identity in visited_dirs:
            return
        visited_dirs.add(identity)
        entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        for entry in entries:
            path = Path(entry.path)
            if entry.is_symlink() and not follow_symlinks:
                continue
            if entry.is_dir(follow_symlinks=follow_symlinks):
                walk(path)
            elif entry.is_file(follow_symlinks=follow_symlinks):
                relative = path.relative_to(base).as_posix()
                manifest[relative] = _file_digest(path, chunk_size)

    walk(base)
    return dict(sorted(manifest.items()))


def compare_manifests(
    before: Mapping[str, str], after: Mapping[str, str]
) -> Dict[str, list[str]]:
    """Classify paths into ``added``, ``removed``, and ``changed`` lists."""
    before_paths, after_paths = set(before), set(after)
    return {
        "added": sorted(after_paths - before_paths),
        "removed": sorted(before_paths - after_paths),
        "changed": sorted(
            path for path in before_paths & after_paths if before[path] != after[path]
        ),
    }


def find_duplicates(manifest: Mapping[str, str]) -> Dict[str, list[str]]:
    """Return content digests mapping to sorted paths with identical content."""
    by_digest = defaultdict(list)
    for path, digest in manifest.items():
        by_digest[digest].append(path)
    return {
        digest: sorted(paths)
        for digest, paths in sorted(by_digest.items())
        if len(paths) > 1
    }
