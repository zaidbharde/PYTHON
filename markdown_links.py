"""Parse Markdown links while ignoring image syntax and fenced code blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass(frozen=True)
class Link:
    text: str
    target: str
    line: int


LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+['\"].*?['\"])?\)")


def extract_links(markdown: str, base_url: str | None = None) -> list[Link]:
    """Extract links from prose, preserving one-based source line numbers."""
    links: list[Link] = []
    in_fence = False
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_PATTERN.finditer(line):
            target = match.group(2)
            if base_url and not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                target = urljoin(base_url, target)
            links.append(Link(match.group(1).strip(), target, line_number))
    return links


def broken_targets(markdown: str, base_url: str | None = None) -> list[str]:
    """Return duplicate link targets, useful for quick document hygiene checks."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for link in extract_links(markdown, base_url):
        if link.target in seen and link.target not in duplicates:
            duplicates.append(link.target)
        seen.add(link.target)
    return duplicates
