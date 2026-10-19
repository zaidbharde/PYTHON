"""Find the minimum raggedness when wrapping words to a fixed line width."""

from __future__ import annotations


def wrap_cost(words: list[str], width: int) -> tuple[int, list[str]]:
    if width <= 0 or any(len(word) > width for word in words):
        raise ValueError("width must fit every word")
    count = len(words)
    best = [float("inf")] * (count + 1)
    choice = [0] * (count + 1)
    best[count] = 0
    for start in range(count - 1, -1, -1):
        line_length = 0
        for end in range(start, count):
            line_length += len(words[end]) + (end > start)
            if line_length > width:
                break
            slack = width - line_length
            penalty = 0 if end == count - 1 else slack * slack
            candidate = penalty + best[end + 1]
            if candidate < best[start]:
                best[start], choice[start] = candidate, end + 1
    lines: list[str] = []
    cursor = 0
    while cursor < count:
        next_cursor = choice[cursor]
        lines.append(" ".join(words[cursor:next_cursor]))
        cursor = next_cursor
    return int(best[0]), lines


if __name__ == "__main__":
    print(wrap_cost("dynamic programs reward careful state design".split(), 16))
