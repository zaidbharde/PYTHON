"""Parse a simple delimited key=value string into a dictionary."""
def parse_pairs(text: str, *, item_separator: str = ",", pair_separator: str = "=") -> dict[str, str]:
    """Trim whitespace; later duplicate keys replace earlier ones."""
    if not item_separator or not pair_separator:
        raise ValueError("separators must not be empty")
    result: dict[str, str] = {}
    for item in text.split(item_separator):
        if not item.strip():
            continue
        key, separator, value = item.partition(pair_separator)
        if not separator or not key.strip():
            raise ValueError(f"invalid key-value item: {item!r}")
        result[key.strip()] = value.strip()
    return result
if __name__ == "__main__":
    assert parse_pairs("a=1, b = two,,a=3") == {"a": "3", "b": "two"}
    print("key-value parser checks passed")
