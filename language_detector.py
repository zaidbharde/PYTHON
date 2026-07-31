from collections import Counter
import math

PROFILES = {
    'English': {
        'the':8.5, 'and':3.0, 'to':2.7, 'of':2.5, 'a':2.3, 'in':2.2,
        'is':1.7, 'it':1.5, 'that':1.4, 'was':1.3, 'for':1.2, 'on':1.0,
        'common_bigrams': ['th','he','in','er','an','re','on','at','en','nd'],
        'avg_word_len': 4.7, 'vowel_ratio': 0.38,
    },
    'Spanish': {
        'de':6.5, 'la':4.5, 'que':3.8, 'el':3.5, 'en':3.3, 'y':3.0,
        'los':2.0, 'del':1.5, 'las':1.4, 'un':1.3, 'por':1.2, 'con':1.0,
        'common_bigrams': ['de','en','el','la','os','es','er','as','al','ar'],
        'avg_word_len': 4.9, 'vowel_ratio': 0.45,
    },
    'French': {
        'de':5.5, 'la':4.0, 'le':3.5, 'et':3.0, 'les':2.8, 'des':2.5,
        'en':2.3, 'un':2.0, 'du':1.5, 'une':1.4, 'que':1.3, 'est':1.2,
        'common_bigrams': ['es','le','de','en','re','on','ou','an','er','ai'],
        'avg_word_len': 4.8, 'vowel_ratio': 0.44,
    },
    'German': {
        'die':5.0, 'der':4.5, 'und':4.0, 'in':3.0, 'den':2.5, 'von':2.0,
        'zu':1.8, 'das':1.7, 'mit':1.5, 'ist':1.4, 'des':1.3, 'auf':1.2,
        'common_bigrams': ['en','er','ch','de','ei','in','nd','ie','ge','st'],
        'avg_word_len': 5.3, 'vowel_ratio': 0.35,
    },
    'Italian': {
        'di':5.5, 'che':4.0, 'la':3.5, 'il':3.3, 'in':3.0, 'e':2.8,
        'del':2.0, 'per':1.8, 'un':1.5, 'una':1.4, 'con':1.3, 'non':1.2,
        'common_bigrams': ['er','re','on','an','in','el','di','en','co','to'],
        'avg_word_len': 4.6, 'vowel_ratio': 0.48,
    },
    'Portuguese': {
        'de':5.0, 'que':4.0, 'o':3.5, 'e':3.0, 'do':2.5, 'da':2.3,
        'em':2.0, 'um':1.8, 'para':1.5, 'com':1.4, 'os':1.3, 'no':1.2,
        'common_bigrams': ['de','os','do','da','em','er','es','en','as','ar'],
        'avg_word_len': 4.7, 'vowel_ratio': 0.46,
    },
}

class LanguageDetector:
    def __init__(self):
        self.profiles = PROFILES

    def _extract_features(self, text):
        text_lower = text.lower()
        words = [w.strip('.,!?;:\'"()[]{}') for w in text_lower.split() if w.strip('.,!?;:\'"()[]{}')]

        if not words:
            return {}

        word_freq = Counter(words)
        total = sum(word_freq.values())
        word_pct = {w: c / total * 100 for w, c in word_freq.items()}

        bigrams = []
        for word in words:
            for i in range(len(word) - 1):
                bigrams.append(word[i:i+2])
        bigram_freq = Counter(bigrams)

        vowels = sum(1 for c in text_lower if c in 'aeiouáéíóúàèìòùäëïöüâêîôûãõ')
        letters = sum(1 for c in text_lower if c.isalpha())
        vowel_ratio = vowels / letters if letters > 0 else 0

        avg_word_len = sum(len(w) for w in words) / len(words)

        return {
            'word_pct': word_pct,
            'bigram_freq': bigram_freq,
            'vowel_ratio': vowel_ratio,
            'avg_word_len': avg_word_len,
            'total_words': len(words),
        }

    def detect(self, text):
        features = self._extract_features(text)
        if not features:
            return []

        scores = {}
        for lang, profile in self.profiles.items():
            score = 0

            for word, expected_pct in profile.items():
                if word in ('common_bigrams', 'avg_word_len', 'vowel_ratio'):
                    continue
                actual = features['word_pct'].get(word, 0)
                score += min(actual, expected_pct) * 10

            for bigram in profile['common_bigrams']:
                if bigram in features['bigram_freq']:
                    score += features['bigram_freq'][bigram] * 2

            word_len_diff = abs(features['avg_word_len'] - profile['avg_word_len'])
            score -= word_len_diff * 5

            vowel_diff = abs(features['vowel_ratio'] - profile['vowel_ratio'])
            score -= vowel_diff * 50

            scores[lang] = max(0, score)

        total = sum(scores.values()) or 1
        results = [(lang, score / total * 100) for lang, score in scores.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def analyze(self, text):
        features = self._extract_features(text)
        results = self.detect(text)

        print(f"\n  {'─' * 55}")
        preview = text[:80].replace('\n', ' ')
        print(f"  Text: \"{preview}{'...' if len(text) > 80 else ''}\"")
        print(f"  Words: {features.get('total_words', 0)} | "
              f"Avg length: {features.get('avg_word_len', 0):.1f} | "
              f"Vowel ratio: {features.get('vowel_ratio', 0):.2f}")

        print(f"\n  Detection results:")
        for lang, confidence in results:
            bar_len = int(confidence / 2)
            bar = '█' * bar_len
            marker = ' ◄─ DETECTED' if confidence == results[0][1] and confidence > 10 else ''
            print(f"    {lang:>12} : {confidence:>5.1f}% {bar}{marker}")

        return results[0][0] if results else "Unknown"


if __name__ == "__main__":
    detector = LanguageDetector()

    texts = {
        'English': "The quick brown fox jumps over the lazy dog. This is a simple test of the language detection system that should work properly.",
        'Spanish': "El rápido zorro marrón salta sobre el perro perezoso. Esta es una prueba simple del sistema de detección de idiomas que debería funcionar correctamente.",
        'French': "Le renard brun rapide saute par dessus le chien paresseux. Ceci est un test simple du système de détection de la langue qui devrait fonctionner correctement.",
        'German': "Der schnelle braune Fuchs springt über den faulen Hund. Dies ist ein einfacher Test des Spracherkennungssystems der richtig funktionieren sollte.",
        'Italian': "La volpe marrone rapida salta sopra il cane pigro. Questo è un semplice test del sistema di rilevamento della lingua che dovrebbe funzionare correttamente.",
        'Portuguese': "A rápida raposa marrom salta sobre o cão preguiçoso. Este é um teste simples do sistema de detecção de idiomas que deve funcionar corretamente.",
    }

    print("=" * 60)
    print("  🌍 Language Detector")
    print("=" * 60)

    correct = 0
    for expected, text in texts.items():
        detected = detector.analyze(text)
        match = detected == expected
        if match:
            correct += 1
        print(f"  Expected: {expected} | Got: {detected} {'✅' if match else '❌'}")

    print(f"\n  Accuracy: {correct}/{len(texts)} ({correct/len(texts)*100:.0f}%)")
