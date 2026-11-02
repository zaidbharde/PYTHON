import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

from safe_zip_extract import safe_extract_zip


class SafeZipExtractTests(unittest.TestCase):
    def test_extracts_nested_files_and_returns_file_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "input.zip"
            destination = root / "out"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("docs/", "")
                output.writestr("docs/readme.txt", "hello\n")
            extracted = safe_extract_zip(archive, destination)
            self.assertEqual(extracted, [destination / "docs/readme.txt"])
            self.assertEqual(extracted[0].read_text(), "hello\n")

    def test_rejects_traversal_and_does_not_extract_earlier_members(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "input.zip"
            destination = root / "out"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("safe/first.txt", "must not be written")
                output.writestr("../outside.txt", "escape")
            with self.assertRaises(ValueError):
                safe_extract_zip(archive, destination)
            self.assertFalse((destination / "safe/first.txt").exists())
            self.assertFalse((root / "outside.txt").exists())

    def test_rejects_absolute_windows_and_backslash_paths(self):
        for name in ("/outside.txt", "C:/outside.txt", "..\\outside.txt", "file.txt:stream"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive = root / "input.zip"
                with zipfile.ZipFile(archive, "w") as output:
                    output.writestr(name, "escape")
                with self.assertRaises(ValueError):
                    safe_extract_zip(archive, root / "out")

    def test_rejects_archive_symlink_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "input.zip"
            link = zipfile.ZipInfo("link")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr(link, "target.txt")
            with self.assertRaises(ValueError):
                safe_extract_zip(archive, root / "out")

    def test_rejects_existing_destination_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "out"
            outside = root / "outside"
            destination.mkdir()
            outside.mkdir()
            (destination / "redirect").symlink_to(outside, target_is_directory=True)
            archive = root / "input.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("redirect/file.txt", "escape")
            with self.assertRaises(ValueError):
                safe_extract_zip(archive, destination)
            self.assertFalse((outside / "file.txt").exists())


if __name__ == "__main__":
    unittest.main()
