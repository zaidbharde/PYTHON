"""Count whitespace-separated words and their frequencies."""
from collections import Counter
import re
def word_count(text: str) -> Counter[str]:
    """Count case-insensitive alphanumeric words, preserving normalized form."""
    return Counter(re.findall(r"[\w']+", text.casefold()))
if __name__ == "__main__":
    counts = word_count("Tea, tea and coffee.")
    assert counts["tea"] == 2 and counts["coffee"] == 1
    print(counts)
