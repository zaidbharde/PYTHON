from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    status: int
    latency_ms: float


def parse_line(line: str) -> Request:
    parts = line.strip().split()
    if len(parts) != 4:
        raise ValueError("expected METHOD PATH STATUS LATENCY_MS")
    method, path, status, latency = parts
    return Request(method.upper(), path, int(status), float(latency))


def summarize(lines: Iterable[str]) -> dict[str, dict[str, float | int]]:
    totals = defaultdict(lambda: {"count": 0, "errors": 0, "latency_ms": 0.0})
    statuses = Counter()
    for line in lines:
        request = parse_line(line)
        bucket = totals[request.path]
        bucket["count"] += 1
        bucket["latency_ms"] += request.latency_ms
        bucket["errors"] += int(request.status >= 500)
        statuses[request.status // 100] += 1
    for bucket in totals.values():
        bucket["latency_ms"] = round(bucket["latency_ms"] / bucket["count"], 2)
    return {"endpoints": dict(totals), "status_classes": dict(statuses)}


if __name__ == "__main__":
    sample = ["GET /health 200 4.2", "GET /items 200 19.5", "POST /items 500 81.0"]
    print(summarize(sample))
