"""Escape text for safe use inside an inline Markdown code span."""
from __future__ import annotations


def escape_inline_code(text: str) -> str:
    """Escape backslashes and backticks in code-span content.

    Markdown code spans treat backslashes literally, so escaping them first
    makes the resulting content unambiguous to readers and downstream tools.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return text.replace("\\", "\\\\").replace("`", "\\`")


class MarkdownCodeEscaper:
    """Small reusable interface for producing escaped inline-code content."""

    @staticmethod
    def escape(text: str) -> str:
        """Return *text* with backslashes and backticks escaped."""
        return escape_inline_code(text)


def _self_check() -> None:
    assert escape_inline_code("") == ""
    assert escape_inline_code("plain text") == "plain text"
    assert escape_inline_code("a`b\\c") == "a\\`b\\\\c"
    assert MarkdownCodeEscaper.escape("```\\") == "\\`\\`\\`\\\\"
    try:
        escape_inline_code(None)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-string input must be rejected")
    print("MarkdownCodeEscaper self-check passed")


if __name__ == "__main__":
    _self_check()
