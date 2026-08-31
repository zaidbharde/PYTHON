from dataclasses import dataclass, field


@dataclass
class Node:
    children: dict[str, "Node"] = field(default_factory=dict)
    frequency: int = 0


class Autocomplete:
    def __init__(self, words: list[tuple[str, int]] = ()):
        self.root = Node()
        for word, frequency in words:
            self.add(word, frequency)

    def add(self, word: str, frequency: int = 1) -> None:
        if not word or frequency < 1:
            raise ValueError("word must be non-empty and frequency positive")
        node = self.root
        for character in word.casefold():
            node = node.children.setdefault(character, Node())
        node.frequency += frequency

    def suggest(self, prefix: str, limit: int = 5) -> list[tuple[str, int]]:
        if limit < 1:
            return []
        node = self.root
        normalized = prefix.casefold()
        for character in normalized:
            if character not in node.children:
                return []
            node = node.children[character]
        matches: list[tuple[str, int]] = []

        def collect(current: Node, suffix: str) -> None:
            if current.frequency:
                matches.append((normalized + suffix, current.frequency))
            for character, child in current.children.items():
                collect(child, suffix + character)

        collect(node, "")
        return sorted(matches, key=lambda item: (-item[1], item[0]))[:limit]


if __name__ == "__main__":
    index = Autocomplete([("rust", 8), ("ruby", 3), ("runner", 5), ("python", 10)])
    print(index.suggest("ru"))
