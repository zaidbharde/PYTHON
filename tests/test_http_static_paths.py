import tempfile
import unittest
from pathlib import Path

from http_framework import HTTPServer


class StaticPathRegressionTests(unittest.TestCase):
    def test_rejects_sibling_with_matching_directory_prefix(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / "public"
            sibling = parent / "public-secret"
            root.mkdir()
            sibling.mkdir()
            (sibling / "secret.txt").write_text("secret")
            server = HTTPServer()
            server.static(str(root))
            self.assertIsNone(server.serve_static("../public-secret/secret.txt"))

    def test_serves_file_inside_static_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "hello.txt").write_text("hello")
            server = HTTPServer()
            server.static(str(root))
            response = server.serve_static("/hello.txt")
            self.assertIsNotNone(response)
            self.assertEqual(response.body, "hello")


if __name__ == "__main__":
    unittest.main()
