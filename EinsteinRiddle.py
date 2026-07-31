"""
Einstein's Riddle (a.k.a. the Zebra Puzzle)
============================================

There are five houses in a row, each with a different color, inhabited by
people of different nationalities, with different pets, drinks, and cigarettes.

Clues
-----
 1. The Brit lives in the red house.
 2. The Swede keeps dogs.
 3. The Dane drinks tea.
 4. The green house is immediately to the left of the white house.
 5. The green house owner drinks coffee.
 6. The person who smokes Pall Mall keeps birds.
 7. The owner of the yellow house smokes Dunhill.
 8. The person living in the center house drinks milk.
 9. The Norwegian lives in the first house.
10. The person who smokes Blend lives next to the one who keeps cats.
11. The person who keeps horses lives next to the Dunhill smoker.
12. The person who smokes BlueMaster drinks beer.
13. The German smokes Prince.
14. The Norwegian lives next to the blue house.
15. The person who smokes Blend has a neighbor who drinks water.

Question: Who owns the fish?
"""

from itertools import permutations
from typing import Optional
from time import perf_counter


# ── Types ─────────────────────────────────────────────────────────────────────
# Each permutation maps a value to a house index (0–4).

House = int                          # 0 = leftmost … 4 = rightmost
Perm = tuple[str, ...]              # a permutation of 5 values across 5 houses

HOUSES = range(5)


# ── Constraint helpers ────────────────────────────────────────────────────────

def at(perm: Perm, value: str) -> House:
    """Return the house index where *value* is placed."""
    return perm.index(value)


def same_house(perm_a: Perm, val_a: str, perm_b: Perm, val_b: str) -> bool:
    """True if val_a and val_b are in the same house."""
    return at(perm_a, val_a) == at(perm_b, val_b)


def neighbors(perm_a: Perm, val_a: str, perm_b: Perm, val_b: str) -> bool:
    """True if val_a and val_b are in adjacent houses."""
    return abs(at(perm_a, val_a) - at(perm_b, val_b)) == 1


def left_of(perm_a: Perm, val_a: str, perm_b: Perm, val_b: str) -> bool:
    """True if val_a is immediately to the left of val_b."""
    return at(perm_a, val_a) == at(perm_b, val_b) - 1


# ── Solver ────────────────────────────────────────────────────────────────────

def solve() -> Optional[dict[str, Perm]]:
    """
    Solve Einstein's riddle using nested generation with early pruning.

    At each nesting level we only generate permutations that satisfy every
    constraint whose variables are already bound.  This reduces the search
    space from ~25 billion to a few thousand checks.

    Returns
    -------
    dict mapping category name → permutation tuple, or None if unsolvable.
    """

    colors = ("red", "green", "white", "yellow", "blue")
    nations = ("brit", "swede", "dane", "norwegian", "german")
    drinks = ("tea", "coffee", "milk", "beer", "water")
    pets = ("dog", "bird", "cat", "horse", "fish")
    smokes = ("pall_mall", "dunhill", "blend", "blue_master", "prince")

    checks = 0

    # ── 1. Colors ─────────────────────────────────────────────────────
    for c in permutations(colors):
        # Clue 4: green is immediately left of white
        if not left_of(c, "green", c, "white"):
            continue

        # ── 2. Nations ────────────────────────────────────────────────
        for n in permutations(nations):
            # Clue 9: Norwegian lives in house 0
            if at(n, "norwegian") != 0:
                continue
            # Clue 1: Brit in red house
            if not same_house(n, "brit", c, "red"):
                continue
            # Clue 14: Norwegian next to blue house
            if not neighbors(n, "norwegian", c, "blue"):
                continue

            # ── 3. Drinks ─────────────────────────────────────────────
            for d in permutations(drinks):
                # Clue 8: milk in center house (index 2)
                if at(d, "milk") != 2:
                    continue
                # Clue 3: Dane drinks tea
                if not same_house(n, "dane", d, "tea"):
                    continue
                # Clue 5: green house → coffee
                if not same_house(c, "green", d, "coffee"):
                    continue

                # ── 4. Smokes ─────────────────────────────────────────
                for s in permutations(smokes):
                    # Clue 13: German smokes Prince
                    if not same_house(n, "german", s, "prince"):
                        continue
                    # Clue 7: yellow house → Dunhill
                    if not same_house(c, "yellow", s, "dunhill"):
                        continue
                    # Clue 12: BlueMaster → beer
                    if not same_house(s, "blue_master", d, "beer"):
                        continue
                    # Clue 15: Blend neighbor drinks water
                    if not neighbors(s, "blend", d, "water"):
                        continue

                    # ── 5. Pets ────────────────────────────────────────
                    for p in permutations(pets):
                        checks += 1

                        # Clue 2: Swede keeps dogs
                        if not same_house(n, "swede", p, "dog"):
                            continue
                        # Clue 6: Pall Mall → birds
                        if not same_house(s, "pall_mall", p, "bird"):
                            continue
                        # Clue 10: Blend neighbor keeps cats
                        if not neighbors(s, "blend", p, "cat"):
                            continue
                        # Clue 11: horse neighbor smokes Dunhill
                        if not neighbors(p, "horse", s, "dunhill"):
                            continue

                        # ── All 15 clues satisfied ────────────────────
                        print(f"   (checked {checks:,} innermost permutations)")
                        return {
                            "color":  c,
                            "nation": n,
                            "drink":  d,
                            "smoke":  s,
                            "pet":    p,
                        }

    return None


# ── Display ───────────────────────────────────────────────────────────────────

def display_solution(solution: dict[str, Perm]) -> None:
    """Pretty-print the solved grid."""
    categories = ["color", "nation", "drink", "smoke", "pet"]

    col_w = 14
    header = "House".center(col_w) + "".join(
        f"{i + 1}".center(col_w) for i in HOUSES
    )
    separator = "─" * len(header)

    print(f"\n{separator}")
    print("  🧩  Einstein's Riddle — Solution")
    print(separator)
    print(header)
    print(separator)

    for cat in categories:
        row = cat.capitalize().center(col_w)
        row += "".join(solution[cat][i].center(col_w) for i in HOUSES)
        print(row)

    print(separator)

    fish_house = at(solution["pet"], "fish")
    owner = solution["nation"][fish_house]
    print(f"\n  🐟  The {owner.capitalize()} owns the fish!  (House {fish_house + 1})\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  Solving Einstein's Riddle…\n")
    start = perf_counter()
    solution = solve()
    elapsed = perf_counter() - start

    if solution is None:
        print("  ❌  No solution found — check the constraints.")
    else:
        display_solution(solution)
        print(f"  ⏱️  Solved in {elapsed:.4f} seconds\n")


if __name__ == "__main__":
    main()
