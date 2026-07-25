import random
import time
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def rand_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

def progress_bar(p, width=32):
    done = int(width * p / 100)
    return "[" + "#" * done + "-" * (width - done) + f"] {p:3d}%"

logs = [
    "Negotiating phantom handshake...",
    "Injecting noise into dead channel...",
    "Reconstructing lost packet signatures...",
    "Decoding mirrored credentials...",
    "Scanning shadow ports...",
    "Spoofing echo layer...",
    "Indexing forgotten hosts...",
    "Capturing synthetic tokens...",
    "Parsing entropy stream...",
    "Syncing anomaly clock..."
]

clear()
print("=== FAKE HACKER TERMINAL SIM ===")
print("All output below is simulated.\n")
time.sleep(1)

targets = [rand_ip() for _ in range(4)]

for t in targets:
    print(f"Target locked: {t}")
    time.sleep(0.5)

print()
time.sleep(1)

for phase in range(10):
    clear()
    print("=== FAKE HACKER TERMINAL SIM ===")
    print("Simulation Mode Active\n")

    current_log = random.choice(logs)
    print("TASK:", current_log)
    print()

    for t in targets:
        p = random.randint(15, 100)
        status = random.choice(["STABLE", "GHOST", "MIRRORED", "DESYNC", "LOCKED"])
        print(f"{t:18} {progress_bar(p)}  {status}")

    print("\nEntropy:", random.randint(1000, 9999))
    print("Ghost Ports:", random.randint(3, 44))
    print("Signal Drift:", f"{random.uniform(0.01, 4.99):.2f}ms")
    time.sleep(0.7)

clear()
print("=== RESULT ===\n")
print("Synthetic breach complete.")
print("Recovered artifact:", random.choice([
    "NULL_KEY_FRAGMENT",
    "ECHO_MAP",
    "SHADOW_TOKEN",
    "CLOCK_DRIFT_TABLE",
    "VOID_SESSION"
]))
