"""
Caesar Cipher — encrypt and decrypt messages by shifting letters.
"""

def encrypt(text: str, shift: int) -> str:
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)


def decrypt(text: str, shift: int) -> str:
    return encrypt(text, -shift)


if __name__ == "__main__":
    message = "Hello, World!"
    shift = 3

    encrypted = encrypt(message, shift)
    decrypted = decrypt(encrypted, shift)

    print(f"Original  : {message}")
    print(f"Encrypted : {encrypted}")
    print(f"Decrypted : {decrypted}")
