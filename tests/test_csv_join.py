"""Regression tests for the standalone streaming CSV join."""

import io
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "source"))

from csv_join import join_csv


class CsvJoinTests(unittest.TestCase):
    def test_matches_and_unmatched_keys(self):
        left = io.StringIO("id,name\n1,Ada\n2,Lin\n")
        right = io.StringIO("ref,score\n1,9\n3,7\n")
        self.assertEqual(list(join_csv(left, right, "id", "ref")), [
            {"id": "1", "name": "Ada", "ref": "1", "score": "9"}
        ])

    def test_duplicate_keys_expand_in_input_order(self):
        left = io.StringIO("id,item\n1,a\n1,b\n")
        right = io.StringIO("ref,tag\n1,x\n1,y\n")
        self.assertEqual(
            [row["item"] + row["tag"] for row in join_csv(left, right, "id", "ref")],
            ["ax", "ay", "bx", "by"],
        )

    def test_left_input_is_consumed_lazily(self):
        class Tracked(io.StringIO):
            def __init__(self, value):
                super().__init__(value)
                self.data_rows_read = 0

            def __next__(self):
                line = super().__next__()
                if self.tell() > len("id,name\n"):
                    self.data_rows_read += 1
                return line

        left = Tracked("id,name\n1,a\n1,b\n")
        rows = join_csv(left, io.StringIO("ref,score\n1,x\n"), "id", "ref")
        self.assertEqual(next(rows)["name"], "a")
        self.assertEqual(left.data_rows_read, 1)

    def test_empty_data_and_header_only(self):
        self.assertEqual(list(join_csv(
            io.StringIO("id,name\n"), io.StringIO("ref,value\n"), "id", "ref"
        )), [])

    def test_missing_key_columns(self):
        with self.assertRaisesRegex(ValueError, "left key column"):
            list(join_csv(io.StringIO("id\na\n"), io.StringIO("ref\na\n"), "absent", "ref"))
        with self.assertRaisesRegex(ValueError, "right key column"):
            list(join_csv(io.StringIO("id\na\n"), io.StringIO("ref\na\n"), "id", "absent"))

    def test_colliding_columns_and_duplicate_headers(self):
        with self.assertRaisesRegex(ValueError, "colliding columns"):
            list(join_csv(io.StringIO("id,x\n1,a\n"), io.StringIO("ref,x\n1,b\n"), "id", "ref"))
        with self.assertRaisesRegex(ValueError, "duplicate column"):
            list(join_csv(io.StringIO("id,id\n1,2\n"), io.StringIO("ref\n1\n"), "id", "ref"))

    def test_missing_headers_and_row_width(self):
        with self.assertRaisesRegex(ValueError, "missing a header"):
            list(join_csv(io.StringIO(""), io.StringIO("ref\n"), "id", "ref"))
        with self.assertRaisesRegex(ValueError, "row width"):
            list(join_csv(io.StringIO("id,name\n1\n"), io.StringIO("ref\n1\n"), "id", "ref"))


if __name__ == "__main__":
    unittest.main()
