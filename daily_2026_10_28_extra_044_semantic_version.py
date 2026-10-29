"""Parse and compare strict three-part semantic versions."""
from dataclasses import dataclass
import re

_VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


@dataclass(frozen=True, order=True)
class SemanticVersion:
    """A minimal SemVer core tuple (major.minor.patch), without prereleases."""

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        if any(type(part) is not int or part < 0 for part in
               (self.major, self.minor, self.patch)):
            raise ValueError("version components must be non-negative integers")

    @classmethod
    def parse(cls, text: str) -> "SemanticVersion":
        """Parse exactly three dot-separated, non-negative integer components."""
        if not isinstance(text, str):
            raise TypeError("version must be a string")
        match = _VERSION.fullmatch(text)
        if match is None:
            raise ValueError(f"invalid semantic version: {text!r}")
        return cls(*(int(part) for part in match.groups()))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


if __name__ == "__main__":
    assert SemanticVersion.parse("1.2.10") > SemanticVersion.parse("1.2.9")
    assert str(SemanticVersion.parse("0.0.0")) == "0.0.0"
    for invalid in ("1.2", "01.2.3", "1.2.3-rc1", "1.2.3 ", "-1.2.3"):
        try:
            SemanticVersion.parse(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid version {invalid!r}")
    print("semantic version checks passed")
