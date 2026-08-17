import random
import string
from collections import Counter
import math
import numpy as np


def generate_alien_signal(length=1000, alphabet_size=7, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    symbols = random.sample(
        string.punctuation + string.ascii_uppercase,
        alphabet_size
    )

    weights = np.random.dirichlet(np.ones(alphabet_size))

    signal = ''.join(
        random.choices(symbols, weights=weights, k=length)
    )

    return signal, symbols


def analyze_frequency(signal):
    count = Counter(signal)
    total = len(signal)

    return {
        char: round(freq / total, 4)
        for char, freq in count.most_common()
    }


def get_ngrams(signal, n=2):
    return Counter(
        signal[i:i + n]
        for i in range(len(signal) - n + 1)
    )


def calculate_entropy(signal):
    count = Counter(signal)
    total = len(signal)

    return -sum(
        (freq / total) * math.log2(freq / total)
        for freq in count.values()
    )


def fake_translate(signal, mapping):
    return ''.join(mapping.get(char, char) for char in signal)


def decode_signal():
    print("\n🛰️ Receiving alien transmission...\n")

    signal, alphabet = generate_alien_signal(
        length=1000,
        alphabet_size=7,
        seed=42
    )

    print("Alien Symbols:", ' '.join(alphabet))
    print("\n📡 Raw Signal:\n")
    print(signal[:200])

    freq = analyze_frequency(signal)

    print("\n📊 Frequency Analysis:")
    for symbol, value in freq.items():
        print(f"  {symbol}: {value:.4f}")

    print("\n🔎 Top Bigrams:")
    bigrams = get_ngrams(signal, 2)

    for pair, count in bigrams.most_common(5):
        print(f"  {pair}: {count}")

    print("\n🔎 Top Trigrams:")
    trigrams = get_ngrams(signal, 3)

    for pattern, count in trigrams.most_common(5):
        print(f"  {pattern}: {count}")

    entropy = calculate_entropy(signal)

    print(f"\n📈 Shannon Entropy: {entropy:.4f} bits")

    sorted_symbols = list(freq.keys())
    english_guess = "ETAOINSHRDLU"

    mapping = dict(
        zip(
            sorted_symbols,
            english_guess[:len(sorted_symbols)]
        )
    )

    translated = fake_translate(
        signal[:200],
        mapping
    )

    print("\n🧬 Translated Sample:")
    print(translated)

    print("\n⚠️ Translation is speculative.")


if __name__ == "__main__":
    decode_signal()
