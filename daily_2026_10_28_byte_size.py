"""Format byte counts using binary units."""
def format_bytes(size: int, precision: int = 1) -> str:
    """Return a readable IEC-style size, preserving a sign if supplied."""
    if precision < 0:
        raise ValueError("precision must be non-negative")
    value = float(size)
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
    index = 0
    while abs(value) >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    number = f"{value:.{precision}f}" if index else str(int(value))
    return f"{number} {units[index]}"
if __name__ == "__main__":
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(-512) == "-512 B"
    print(format_bytes(5_000_000))
