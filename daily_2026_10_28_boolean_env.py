"""Parse common human-readable boolean environment values."""
_TRUE = {"1", "true", "yes", "on", "enabled"}
_FALSE = {"0", "false", "no", "off", "disabled"}
def parse_bool(value: str, *, default: bool | None = None) -> bool:
    """Convert a conventional boolean string or reject an unknown value."""
    normalized = value.strip().lower()
    if normalized in _TRUE:
        return True
    if normalized in _FALSE:
        return False
    if default is not None:
        return default
    raise ValueError(f"not a recognized boolean: {value!r}")
if __name__ == "__main__":
    assert parse_bool(" YES ") and not parse_bool("off")
    assert parse_bool("maybe", default=False) is False
    print("boolean parsing checks passed")
