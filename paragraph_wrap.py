"""Width-aware paragraph wrapping that preserves blank lines and prefixes."""

from __future__ import annotations

import textwrap


def wrap_document(document: str, width: int = 72) -> str:
    """Wrap each paragraph independently and retain intentional blank lines."""
    if width < 16:
        raise ValueError("width must leave room for readable text")
    paragraphs = document.split("\n\n")
    wrapped: list[str] = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped.append("")
            continue
        lines = paragraph.splitlines()
        prefix = lines[0][: len(lines[0]) - len(lines[0].lstrip())]
        body = " ".join(line.strip() for line in lines).strip()
        chunks = textwrap.wrap(body, width=width - len(prefix), break_long_words=False, break_on_hyphens=False)
        wrapped.append("\n".join(prefix + chunk for chunk in chunks))
    return "\n\n".join(wrapped)


if __name__ == "__main__":
    print(wrap_document("  A compact paragraph can be reflowed without losing its indentation.", 40))
