from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CommitSummary:
    repository: str
    commit_hash: str
    filename: str
    lines: int
    verified: bool

    def as_text(self) -> str:
        status = "verified" if self.verified else "needs review"
        return f"{self.repository}: {self.filename} ({self.lines} lines, {status}) [{self.commit_hash[:12]}]"


def render_report(commits: list[CommitSummary], generated_at: datetime | None = None) -> str:
    timestamp = generated_at or datetime.now(timezone.utc)
    verified = sum(commit.verified for commit in commits)
    header = [
        "Manual commit notification test",
        f"Generated: {timestamp.isoformat()}",
        f"Commits reported: {len(commits)}",
        f"Verified entries: {verified}/{len(commits)}",
        "",
    ]
    return "\n".join(header + [commit.as_text() for commit in commits])


if __name__ == "__main__":
    sample = CommitSummary("zaidbharde/PYTHON", "demo-hash", __file__, 28, True)
    print(render_report([sample]))
