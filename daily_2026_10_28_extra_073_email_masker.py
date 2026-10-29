"""Mask an email's local part while leaving its domain visible."""

import re


def mask_email(address: str) -> str:
    """Return an address with its local part masked; invalid input raises ValueError.

    The first local-part character remains visible, and the remainder is replaced
    with asterisks. The domain is preserved exactly as supplied.
    """
    if not isinstance(address, str):
        raise ValueError("email address must be a string")
    if not address or address != address.strip() or any(c.isspace() for c in address):
        raise ValueError("email address must be non-empty and contain no whitespace")
    if address.count("@") != 1:
        raise ValueError("email address must contain exactly one @")

    local, domain = address.rsplit("@", 1)
    atom = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    if (len(address) > 254 or len(local) > 64 or
            not re.fullmatch(rf"{atom}(?:\.{atom})*", local)):
        raise ValueError("invalid email local part")
    labels = domain.split(".")
    if (not domain or len(domain) > 253 or len(labels) < 2 or
            any(not label or len(label) > 63 or
                not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
                for label in labels)):
        raise ValueError("invalid email domain")

    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"


if __name__ == "__main__":
    assert mask_email("alice.smith@example.com") == "a**********@example.com"
    assert mask_email("x@sub.example.org") == "x@sub.example.org"
    assert mask_email("A+b@EXAMPLE.COM") == "A**@EXAMPLE.COM"
    for invalid in ("", " alice@example.com", "a@@b.com", "@example.com",
                    "a..b@example.com", "a@localhost", "a@-bad.example"):
        try:
            mask_email(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid address accepted: {invalid!r}")
    print("Email masker self-check passed")
