"""Build a conservative portable filename from an arbitrary label."""
import re
_INVALID = re.compile(r"[^A-Za-z0-9._-]+")
def safe_filename(label: str, *, fallback: str = "file") -> str:
    """Replace unsafe runs, trim punctuation, and avoid empty names."""
    name = _INVALID.sub("_", label.strip()).strip("._-")
    return name or fallback
if __name__ == "__main__":
    assert safe_filename("  report: Q4/2026  ") == "report_Q4_2026"
    assert safe_filename("...!!!") == "file"
    print("filename checks passed")
