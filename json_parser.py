"""A small recursive-descent JSON parser."""

import json
import re


class JSONParseError(ValueError):
    """Raised when input is not a valid JSON document."""


def parse_json(s):
    if not isinstance(s, str):
        raise TypeError("JSON input must be a string")

    def fail(message, position):
        raise JSONParseError(f"{message} at position {position}")

    def whitespace(i):
        while i < len(s) and s[i] in " \t\n\r":
            i += 1
        return i

    def parse_string(i):
        start = i
        i += 1
        escaped = False
        while i < len(s):
            char = s[i]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                try:
                    return json.loads(s[start:i + 1]), i + 1
                except json.JSONDecodeError as exc:
                    fail(f"invalid string ({exc.msg})", start + exc.pos)
            elif ord(char) < 0x20:
                fail("unescaped control character in string", i)
            i += 1
        fail("unterminated string", start)

    def parse_value(i):
        i = whitespace(i)
        if i >= len(s):
            fail("expected a value", i)
        char = s[i]
        if char == '"':
            return parse_string(i)
        if char == "{":
            return parse_object(i)
        if char == "[":
            return parse_array(i)
        for token, value in (("true", True), ("false", False), ("null", None)):
            if s.startswith(token, i):
                return value, i + len(token)
        match = re.match(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", s[i:])
        if match:
            token = match.group(0)
            try:
                value = float(token) if any(c in token for c in ".eE") else int(token)
            except ValueError:
                fail("invalid number", i)
            return value, i + len(token)
        fail("expected a JSON value", i)

    def parse_object(i):
        result = {}
        i = whitespace(i + 1)
        if i < len(s) and s[i] == "}":
            return result, i + 1
        while True:
            if i >= len(s) or s[i] != '"':
                fail("expected an object key string", i)
            key, i = parse_string(i)
            i = whitespace(i)
            if i >= len(s) or s[i] != ":":
                fail("expected ':' after object key", i)
            value, i = parse_value(i + 1)
            result[key] = value
            i = whitespace(i)
            if i < len(s) and s[i] == "}":
                return result, i + 1
            if i >= len(s) or s[i] != ",":
                fail("expected ',' or '}' in object", i)
            i = whitespace(i + 1)

    def parse_array(i):
        result = []
        i = whitespace(i + 1)
        if i < len(s) and s[i] == "]":
            return result, i + 1
        while True:
            value, i = parse_value(i)
            result.append(value)
            i = whitespace(i)
            if i < len(s) and s[i] == "]":
                return result, i + 1
            if i >= len(s) or s[i] != ",":
                fail("expected ',' or ']' in array", i)
            i = whitespace(i + 1)

    value, end = parse_value(0)
    end = whitespace(end)
    if end != len(s):
        fail("unexpected trailing data", end)
    return value


if __name__ == "__main__":
    data = '{"name": "Zaid", "age": 22, "skills": ["Java", "Python"], "active": true}'
    print(parse_json(data))
