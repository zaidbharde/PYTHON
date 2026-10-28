"""Convert IPv4 dotted-decimal addresses to and from integers."""
def ipv4_to_int(address: str) -> int:
    parts = address.split(".")
    if len(parts) != 4:
        raise ValueError("IPv4 address must have four octets")
    number = 0
    for part in parts:
        if not part.isdecimal() or not 0 <= int(part) <= 255:
            raise ValueError(f"invalid IPv4 octet: {part!r}")
        number = (number << 8) | int(part)
    return number
def int_to_ipv4(number: int) -> str:
    if not 0 <= number <= 0xFFFFFFFF:
        raise ValueError("integer outside IPv4 range")
    return ".".join(str((number >> shift) & 255) for shift in (24, 16, 8, 0))
if __name__ == "__main__":
    assert int_to_ipv4(ipv4_to_int("192.0.2.1")) == "192.0.2.1"
    print("IPv4 conversion checks passed")
