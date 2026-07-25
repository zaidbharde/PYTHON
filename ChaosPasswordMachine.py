import secrets
import string
import math

rng = secrets.SystemRandom()

starts = ["ka", "zu", "re", "xo", "ni", "va", "ty", "mo", "shi", "dra", "tek", "zen"]
mids = ["ra", "ki", "lo", "mi", "to", "za", "xe", "nu", "fi", "qu", "vo", "sha"]
ends = ["n", "x", "th", "r", "z", "k", "m", "q", "v", "s"]
symbols = "!@#$%^&*_-+=?"
digits = string.digits
uppers = string.ascii_uppercase

def make_password(length=16):
    parts = []

    while len("".join(parts)) < length - 4:
        chunk = rng.choice(starts) + rng.choice(mids) + rng.choice(ends)
        parts.append(chunk)

    base = "".join(parts)[:length - 4]
    extra = [
        rng.choice(symbols),
        rng.choice(digits),
        rng.choice(uppers),
        rng.choice(digits + symbols + uppers)
    ]

    pw = list(base + "".join(extra))
    rng.shuffle(pw)
    return "".join(pw[:length])

def entropy_estimate(password):
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in symbols for c in password):
        pool += len(symbols)
    return round(len(password) * math.log2(pool), 2) if pool else 0

length = input("Password length (default 16): ").strip()
length = int(length) if length.isdigit() and int(length) >= 8 else 16

count = input("Kitne chahiye? (default 5): ").strip()
count = int(count) if count.isdigit() and int(count) > 0 else 5

print("\n=== CHAOS PASSWORD MACHINE ===\n")
for i in range(count):
    pw = make_password(length)
    print(f"{i+1}. {pw}   | entropy ~ {entropy_estimate(pw)} bits")
