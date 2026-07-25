import random
import time
import os

GLITCH_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*?!/\\|[]{}<>~")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def glitch_text(text, intensity):
    out = []
    for ch in text:
        if ch == " ":
            out.append(" ")
        elif random.random() < intensity:
            out.append(random.choice(GLITCH_CHARS))
        else:
            out.append(ch)
    return "".join(out)

text = input("Text daal: ").strip() or "REALITY IS BROKEN"

try:
    for cycle in range(6):
        for i in range(12, -1, -1):
            intensity = i / 12
            clear()
            print("=== GLITCH TEXT ANIMATOR ===\n")
            print(glitch_text(text, intensity))
            time.sleep(0.07)

        for i in range(0, 13):
            intensity = i / 12
            clear()
            print("=== GLITCH TEXT ANIMATOR ===\n")
            print(glitch_text(text, intensity))
            time.sleep(0.07)

    clear()
    print("=== FINAL OUTPUT ===\n")
    print(text)

except KeyboardInterrupt:
    print("\nStopped.")
