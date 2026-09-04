"""Find unmatched brackets while ignoring strings and comments."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Problem:
    position: int
    message: str

PAIRS = {")": "(", "]": "[", "}": "{"}
OPENERS = set(PAIRS.values())


def lint(source: str) -> list[Problem]:
    stack: list[tuple[str, int]] = []
    problems: list[Problem] = []
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(source):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in "'\"":
            quote = char
        elif char == "#":
            newline = source.find("\n", index)
            index = len(source) if newline < 0 else newline
            continue
        elif char in OPENERS:
            stack.append((char, index))
        elif char in PAIRS:
            if not stack or stack[-1][0] != PAIRS[char]:
                problems.append(Problem(index, f"unexpected {char!r}"))
            else:
                stack.pop()
        index += 1
    problems.extend(Problem(pos, f"unclosed {char!r}") for char, pos in stack)
    if quote:
        problems.append(Problem(len(source), "unterminated string"))
    return problems


if __name__ == "__main__":
    import sys
    for problem in lint(sys.stdin.read()):
        print(f"{problem.position}: {problem.message}")
