"""Regression tests for content_manifest."""

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# The deliverable keeps source and tests in sibling directories.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))

from content_manifest import build_manifest, compare_manifests, find_duplicates


class ContentManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_nested_empty_identical_and_deterministic_paths(self):
        (self.root / "z.txt").write_bytes(b"same")
        (self.root / "empty").write_bytes(b"")
        nested = self.root / "a" / "deep"
        nested.mkdir(parents=True)
        (nested / "copy.txt").write_bytes(b"same")
        expected = {
            "a/deep/copy.txt": hashlib.sha256(b"same").hexdigest(),
            "empty": hashlib.sha256(b"").hexdigest(),
            "z.txt": hashlib.sha256(b"same").hexdigest(),
        }
        result = build_manifest(self.root)
        self.assertEqual(result, expected)
        self.assertEqual(list(result), sorted(result))
        self.assertEqual(find_duplicates(result), {hashlib.sha256(b"same").hexdigest(): ["a/deep/copy.txt", "z.txt"]})

    def test_compare_added_removed_changed_and_identical(self):
        self.assertEqual(
            compare_manifests({"same": "a", "changed": "old", "gone": "x"},
                              {"same": "a", "changed": "new", "new": "b"}),
            {"added": ["new"], "removed": ["gone"], "changed": ["changed"]},
        )

    def test_reads_in_bounded_chunks(self):
        (self.root / "large").write_bytes(b"0123456789")
        real_open = open
        sizes = []

        class Reader:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def read(self, size=-1):
                sizes.append(size)
                return self.stream.read(size)

        def tracked_open(path, mode="r", *args, **kwargs):
            stream = real_open(path, mode, *args, **kwargs)
            return Reader(stream) if Path(path) == self.root / "large" else stream

        with mock.patch("builtins.open", side_effect=tracked_open):
            build_manifest(self.root, chunk_size=3)
        self.assertEqual(sizes, [3, 3, 3, 3, 3])

    def test_symlinks_are_skipped_by_default_and_followed_on_request(self):
        target = self.root / "target"
        target.write_text("payload", encoding="utf-8")
        (self.root / "file-link").symlink_to(target)
        linked_dir = self.root / "dir-link"
        linked_dir.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(list(build_manifest(self.root)), ["target"])
        followed = build_manifest(self.root, follow_symlinks=True)
        self.assertIn("file-link", followed)
        self.assertEqual(followed["file-link"], followed["target"])
        self.assertNotIn("dir-link/target", followed)  # cycle is not traversed

    def test_missing_root_and_non_directory(self):
        with self.assertRaises(FileNotFoundError):
            build_manifest(self.root / "missing")
        file_path = self.root / "file"
        file_path.touch()
        with self.assertRaises(NotADirectoryError):
            build_manifest(file_path)

    def test_invalid_chunk_size(self):
        with self.assertRaises(ValueError):
            build_manifest(self.root, chunk_size=0)

    def test_changed_bytes_change_digest(self):
        path = self.root / "item"
        path.write_bytes(b"first")
        first = build_manifest(self.root)
        path.write_bytes(b"other")
        second = build_manifest(self.root)
        self.assertEqual(compare_manifests(first, second)["changed"], ["item"])


if __name__ == "__main__":
    unittest.main()
