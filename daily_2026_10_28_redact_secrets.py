"""Redact values for common key-value secret labels in text."""
import re
_SECRET = re.compile(r"\b(password|passwd|token|api[_-]?key|secret)(\s*[=:]\s*)([^\s,;]+)", re.IGNORECASE)
def redact_secrets(text: str, replacement: str = "[REDACTED]") -> str:
    """Mask likely credentials while retaining their labels and separators."""
    return _SECRET.sub(lambda match: match.group(1) + match.group(2) + replacement, text)
if __name__ == "__main__":
    assert redact_secrets("token=abc api_key:xyz") == "token=[REDACTED] api_key:[REDACTED]"
    print("credential redaction checks passed")
