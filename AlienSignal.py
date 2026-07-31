import random
import string
from collections import Counter
import numpy as np

# Step 1: Simulate alien signal
def generate_alien_signal(length=1000, alphabet_size=7):
    symbols = random.sample(string.punctuation + string.ascii_uppercase, alphabet_size)
    weights = np.random.dirichlet(np.ones(alphabet_size), size=1)[0]  # random frequency bias
    signal = ''.join(random.choices(symbols, weights=weights, k=length))
    return signal, symbols

# Step 2: Frequency analysis
def analyze_frequency(signal):
    count = Counter(signal)
    total = len(signal)
    return {char: round(freq / total, 4) for char, freq in count.items()}

# Step 3: N-gram analysis
def get_ngrams(signal, n=2):
    return Counter([signal[i:i+n] for i in range(len(signal)-n+1)])

# Step 4: Simulated symbol replacement (just to show 'translation idea')
def fake_translate(signal, mapping):
    return ''.join([mapping.get(c, c) for c in signal])

# Step 5: Run full analysis
def decode_signal():
    print("\n🛰️  Receiving alien transmission...\n")
    signal, alien_alphabet = generate_alien_signal()
    print("Alien Symbols Used:", ' '.join(alien_alphabet))
    print("\n📡 Raw Signal Sample (first 200 chars):\n", signal[:200], "\n")

    print("📊 Frequency Analysis:")
    freq = analyze_frequency(signal)
    for sym, f in freq.items():
        print(f"  {sym}: {f}")

    print("\n🔎 Bigram Pattern Snippets:")
    bigrams = get_ngrams(signal, n=2)
    for pair, count in bigrams.most_common(5):
        print(f"  {pair}: {count} times")

    print("\n🧪 Attempting pattern decryption...\n")

    # Fake decryption using most common to least common substitution
    sorted_symbols = [item[0] for item in sorted(freq.items(), key=lambda x: -x[1])]
    english_guess = list("ETAOINSHRDLC")[:len(sorted_symbols)]
    guess_map = dict(zip(sorted_symbols, english_guess))
    
    translated = fake_translate(signal[:200], guess_map)
    print("🧬 Translated Sample:\n", translated)
    print("\n(Disclaimer: Translation is speculative. Alien context unknown.)")

# Run it
decode_signal()
