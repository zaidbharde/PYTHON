import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "http_byte_ranges.py"
SPEC = importlib.util.spec_from_file_location("http_byte_ranges", SOURCE)
http_byte_ranges = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(http_byte_ranges)
parse_byte_ranges = http_byte_ranges.parse_byte_ranges
UnsatisfiableRangeError = http_byte_ranges.UnsatisfiableRangeError


class ByteRangeTests(unittest.TestCase):
    def test_closed_open_and_suffix_ranges(self):
        self.assertEqual(parse_byte_ranges("bytes=2-5", 10), [(2, 5)])
        self.assertEqual(parse_byte_ranges("bytes=7-", 10), [(7, 9)])
        self.assertEqual(parse_byte_ranges("bytes=-3", 10), [(7, 9)])

    def test_end_is_clamped_and_oversized_suffix_selects_whole_resource(self):
        self.assertEqual(parse_byte_ranges("bytes=8-99", 10), [(8, 9)])
        self.assertEqual(parse_byte_ranges("bytes=-99", 10), [(0, 9)])

    def test_multiple_ranges_and_unsatisfiable_members(self):
        self.assertEqual(parse_byte_ranges("bytes=0-1, 5-6, 99-100", 10), [(0, 1), (5, 6)])

    def test_deterministic_coalescing_of_adjacent_and_overlapping_ranges(self):
        header = "bytes=8-9, 1-3, 3-5, 7-7"
        self.assertEqual(parse_byte_ranges(header, 10), [(1, 5), (7, 9)])
        self.assertEqual(parse_byte_ranges(header, 10), [(1, 5), (7, 9)])
        self.assertEqual(parse_byte_ranges(header, 10, coalesce=False), [(1, 3), (3, 5), (7, 7), (8, 9)])

    def test_malformed_syntax_and_unsupported_unit(self):
        for header in ("bytes=", "bytes=1", "bytes=-", "bytes=1-2,,3-4", "bytes=3-1", "items=0-1", "bytes=1-2=3"):
            with self.subTest(header=header):
                if header == "bytes=3-1":
                    with self.assertRaises(UnsatisfiableRangeError):
                        parse_byte_ranges(header, 10)
                else:
                    with self.assertRaises(ValueError):
                        parse_byte_ranges(header, 10)

    def test_zero_length_and_unsatisfiable_request(self):
        for header in ("bytes=0-", "bytes=-5"):
            with self.subTest(header=header):
                with self.assertRaises(UnsatisfiableRangeError):
                    parse_byte_ranges(header, 0)
        with self.assertRaises(UnsatisfiableRangeError):
            parse_byte_ranges("bytes=12-20", 10)
        self.assertEqual(parse_byte_ranges("bytes=12-20, 2-3", 10), [(2, 3)])

    def test_argument_validation(self):
        for length in (-1, True, 1.5):
            with self.subTest(length=length):
                with self.assertRaises((TypeError, ValueError)):
                    parse_byte_ranges("bytes=0-1", length)
        with self.assertRaises(TypeError):
            parse_byte_ranges(None, 1)


if __name__ == "__main__":
    unittest.main()
