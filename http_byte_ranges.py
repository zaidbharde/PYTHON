"""Parse and normalize HTTP byte-range request headers.

Ranges are represented as inclusive ``(start, end)`` pairs. Malformed headers
raise ValueError; headers containing no satisfiable ranges raise
UnsatisfiableRangeError (a ValueError subclass).
"""

import re


class UnsatisfiableRangeError(ValueError):
    """Raised when a valid byte-range set selects no bytes in the resource."""


_RANGE_RE = re.compile(r"([0-9]*)-([0-9]*)\Z", re.ASCII)


def parse_byte_ranges(header, resource_length, *, coalesce=True):
    """Return normalized inclusive byte intervals from a Range header.

    The supported unit is ``bytes``. Unsatisfiable members are ignored when
    other members can be served, as required for byte-range sets. Adjacent or
    overlapping intervals are merged by default, with stable sorted output.
    """
    if not isinstance(header, str):
        raise TypeError("header must be a string")
    if isinstance(resource_length, bool) or not isinstance(resource_length, int):
        raise TypeError("resource_length must be an integer")
    if resource_length < 0:
        raise ValueError("resource_length must not be negative")

    value = header.strip()
    if "=" not in value:
        raise ValueError("malformed Range header")
    unit, spec = value.split("=", 1)
    if unit.strip().lower() != "bytes" or "=" in spec:
        raise ValueError("unsupported or malformed Range unit")
    if not spec or not spec.strip():
        raise ValueError("empty byte-range set")

    intervals = []
    for member in spec.split(","):
        member = member.strip()
        match = _RANGE_RE.fullmatch(member)
        if match is None or not any(match.groups()):
            raise ValueError("malformed byte-range member: {!r}".format(member))
        first, last = match.groups()
        if first:
            start = int(first)
            end = int(last) if last else resource_length - 1
            if start > end or start >= resource_length:
                continue
            intervals.append((start, min(end, resource_length - 1)))
        else:
            suffix_length = int(last)
            if suffix_length == 0 or resource_length == 0:
                continue
            intervals.append((max(0, resource_length - suffix_length), resource_length - 1))

    if not intervals:
        raise UnsatisfiableRangeError("no requested byte ranges are satisfiable")
    intervals.sort()
    if not coalesce:
        return intervals

    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
