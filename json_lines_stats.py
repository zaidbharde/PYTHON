import json
from collections import Counter
from io import StringIO


def summarize(stream):
    levels = Counter()
    durations = []
    for line in stream:
        record = json.loads(line)
        levels[record.get("level", "unknown")] += 1
        if isinstance(record.get("duration_ms"), (int, float)):
            durations.append(record["duration_ms"])
    return {
        "events": sum(levels.values()),
        "levels": dict(levels),
        "average_ms": round(sum(durations) / len(durations), 2) if durations else 0,
    }


if __name__ == "__main__":
    sample = StringIO('{"level":"info","duration_ms":12}
{"level":"error"}
')
    print(summarize(sample))
