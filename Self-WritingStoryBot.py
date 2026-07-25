import random
import textwrap

heroes = ["Aarav", "Zoya", "Kabir", "Mira", "Ishaan", "Noor"]
places = ["abandoned moon station", "desert city", "underwater temple", "floating library", "broken timeline", "glass forest"]
objects = ["black compass", "singing key", "time seed", "mirror blade", "silent radio", "gravity coin"]
threats = ["memory thief", "sleep virus", "shadow king", "echo beast", "void storm", "mechanical prophet"]
twists = [
    "the hero was the missing map all along",
    "time had been looping for 900 days",
    "the enemy was protecting the world",
    "the object only worked when forgotten",
    "the city existed inside a dream",
    "the final door opened backward through memory"
]
endings = [
    "the sky rebooted at dawn",
    "all names vanished except one",
    "the ocean rose into the stars",
    "every clock stopped and then smiled",
    "history rewrote itself in gold dust",
    "the world remained broken, but alive"
]

hero = input("Hero name (blank = random): ").strip() or random.choice(heroes)

story = [
    f"{hero} woke up inside the {random.choice(places)} with a {random.choice(objects)} in one hand and someone else's last warning in the other.",
    f"Before sunrise, a {random.choice(threats)} began hunting every person who remembered the old world.",
    f"To survive, {hero} traded a secret for direction and followed a staircase that should not have existed.",
    f"At the center of everything, {random.choice(twists)}.",
    f"In the end, {random.choice(endings)}."
]

print("\n=== STORY BOT OUTPUT ===\n")
for line in story:
    print(textwrap.fill(line, width=72))
    print()
