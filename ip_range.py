"""Normalize and merge network ranges for compact allowlists."""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable


def merge_ranges(networks: Iterable[str]) -> list[str]:
    """Return sorted CIDR ranges after removing covered and overlapping blocks."""
    parsed = sorted(
        (ipaddress.ip_network(value, strict=False) for value in networks),
        key=lambda net: (net.version, int(net.network_address), -net.prefixlen),
    )
    merged: list[ipaddress._BaseNetwork] = []
    for network in parsed:
        if any(network.subnet_of(existing) for existing in merged):
            continue
        merged = [existing for existing in merged if not existing.subnet_of(network)]
        merged.append(network)
    return [str(network) for network in sorted(merged, key=lambda net: (net.version, int(net.network_address), net.prefixlen))]


if __name__ == "__main__":
    sample = ["10.0.1.0/24", "10.0.0.0/24", "10.0.0.0/16", "192.0.2.4/32"]
    print("\n".join(merge_ranges(sample)))
