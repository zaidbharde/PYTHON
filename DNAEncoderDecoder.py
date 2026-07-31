DNA_MAP = {
    "00": "A",
    "01": "C",
    "10": "G",
    "11": "T"
}

REV_MAP = {v: k for k, v in DNA_MAP.items()}

def text_to_dna(text):
    raw = text.encode("utf-8")
    bits = "".join(f"{b:08b}" for b in raw)
    dna = "".join(DNA_MAP[bits[i:i+2]] for i in range(0, len(bits), 2))
    return dna

def dna_to_text(dna):
    dna = dna.upper().strip()

    if any(ch not in "ACGT" for ch in dna):
        raise ValueError("DNA string me sirf A, C, G, T hone chahiye.")

    if len(dna) % 4 != 0:
        raise ValueError("DNA length valid nahi hai. 1 byte = 4 DNA chars.")

    bits = "".join(REV_MAP[ch] for ch in dna)
    raw = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    return raw.decode("utf-8")

while True:
    print("\n=== DNA ENCODER / DECODER ===")
    print("1. Text -> DNA")
    print("2. DNA -> Text")
    print("3. Exit")

    choice = input("Choose: ").strip()

    if choice == "1":
        text = input("Text daal: ")
        print("DNA:", text_to_dna(text))

    elif choice == "2":
        dna = input("DNA daal: ")
        try:
            print("Text:", dna_to_text(dna))
        except Exception as e:
            print("Error:", e)

    elif choice == "3":
        break

    else:
        print("Invalid choice")
