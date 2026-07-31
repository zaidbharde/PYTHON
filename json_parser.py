def parse_json(s):
    def skip_whitespace(i):
        while i < len(s) and s[i] in " \t\n\r":
            i += 1
        return i

    def parse_value(i):
        i = skip_whitespace(i)
        if s[i] == '{': return parse_object(i)
        if s[i] == '[': return parse_array(i)
        if s[i] == '"': return parse_string(i)
        if s[i:i+4] == 'true': return True, i + 4
        if s[i:i+5] == 'false': return False, i + 5
        if s[i:i+4] == 'null': return None, i + 4
        return parse_number(i)

    def parse_object(i):
        obj = {}
        i += 1
        i = skip_whitespace(i)
        if s[i] == '}': return obj, i + 1
        while True:
            i = skip_whitespace(i)
            key, i = parse_string(i)
            i = skip_whitespace(i)
            i += 1  # skip ':'
            value, i = parse_value(i)
            obj[key] = value
            i = skip_whitespace(i)
            if s[i] == ',': i += 1
            elif s[i] == '}': return obj, i + 1

    def parse_array(i):
        arr = []
        i += 1
        i = skip_whitespace(i)
        if s[i] == ']': return arr, i + 1
        while True:
            value, i = parse_value(i)
            arr.append(value)
            i = skip_whitespace(i)
            if s[i] == ',': i += 1
            elif s[i] == ']': return arr, i + 1

    def parse_string(i):
        i += 1
        start = i
        while s[i] != '"':
            i += 1
        return s[start:i], i + 1

    def parse_number(i):
        start = i
        while i < len(s) and (s[i].isdigit() or s[i] in ".-"):
            i += 1
        num_str = s[start:i]
        return (float(num_str) if '.' in num_str else int(num_str)), i

    value, _ = parse_value(0)
    return value


if __name__ == "__main__":
    data = '{"name": "Zaid", "age": 22, "skills": ["Java", "Python"], "active": true}'
    result = parse_json(data)
    print(result)
