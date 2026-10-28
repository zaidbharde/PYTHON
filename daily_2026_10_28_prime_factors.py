"""Return prime factors of an integer with multiplicity."""
def prime_factors(number: int) -> list[int]:
    if number < 2:
        return []
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors.append(divisor)
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if number > 1:
        factors.append(number)
    return factors
if __name__ == "__main__":
    assert prime_factors(360) == [2, 2, 2, 3, 3, 5]
    assert prime_factors(1) == []
    print("factorization checks passed")
