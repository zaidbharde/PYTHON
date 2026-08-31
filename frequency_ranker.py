from collections import Counter
from collections.abc import Iterable


def rank_terms(terms: Iterable[str], limit: int | None = None) -> list[tuple[str, int]]:
    counts = Counter(term.casefold() for term in terms if term.strip())
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked if limit is None else ranked[:max(0, limit)]


def rank_text(text: str, limit: int | None = None) -> list[tuple[str, int]]:
    words = (token.strip(".,!?;:()[]{}\"'") for token in text.split())
    return rank_terms((word for word in words if word), limit)


if __name__ == "__main__":
    document = "Cache data quickly; cache data safely; data should be observable."
    print(rank_text(document, limit=4))
