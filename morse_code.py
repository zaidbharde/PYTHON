MORSE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',  '0': '-----', '1': '.----',
    '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/',     '.': '.-.-.-', ',': '--..--', '?': '..--..',
}

REVERSE = {v: k for k, v in MORSE.items()}

def encode(text):
    return ' '.join(MORSE.get(c, '') for c in text.upper())

def decode(morse):
    return ''.join(REVERSE.get(c, '') for c in morse.split(' '))

if __name__ == "__main__":
    tests = ["Hello World", "SOS", "Python 3.12", "ATTACK AT DAWN"]

    print("=" * 50)
    print("  Morse Code Encoder/Decoder")
    print("=" * 50)

    for text in tests:
        encoded = encode(text)
        decoded = decode(encoded)
        print(f"\n  Text    : {text}")
        print(f"  Morse   : {encoded}")
        print(f"  Decoded : {decoded}")
        print(f"  Match   : {'✅' if decoded == text.upper() else '❌'}")
