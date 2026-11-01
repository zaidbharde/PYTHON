import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
from json_parser import JSONParseError, parse_json


class ParseJSONTests(unittest.TestCase):
    def test_escaped_quote(self):
        self.assertEqual(parse_json(r'{"x":"a\"b"}'), {"x": 'a"b'})

    def test_escaped_backslash(self):
        self.assertEqual(parse_json(r'{"x":"a\\b"}'), {"x": "a\\b"})

    def test_all_json_escapes_and_unicode(self):
        self.assertEqual(
            parse_json(r'"\"\\\/\b\f\n\r\t\u263A"'),
            '"\\/\b\f\n\r\t☺',
        )

    def test_nested_values_and_plain_string(self):
        self.assertEqual(
            parse_json('{"items":[1,true,null,{"name":"plain"}],"ok":false}'),
            {"items": [1, True, None, {"name": "plain"}], "ok": False},
        )
        self.assertEqual(parse_json('"ordinary"'), "ordinary")

    def test_empty_and_boundary_strings(self):
        self.assertEqual(parse_json('""'), "")
        self.assertEqual(parse_json(r'"\\"'), "\\")

    def test_malformed_escape_is_parse_error(self):
        for text in ('"\\q"', '"\\u12G4"', '"line\nbreak"'):
            with self.subTest(text=text), self.assertRaises(JSONParseError):
                parse_json(text)

    def test_unterminated_and_dangling_escape_are_parse_errors(self):
        for text in ('"unfinished', '"unfinished\\'):
            with self.subTest(text=text), self.assertRaises(JSONParseError):
                parse_json(text)

    def test_truncated_and_trailing_data_are_parse_errors(self):
        for text in ('', '{', '[1,', '"x" trailing'):
            with self.subTest(text=text), self.assertRaises(JSONParseError):
                parse_json(text)


if __name__ == "__main__":
    unittest.main()
