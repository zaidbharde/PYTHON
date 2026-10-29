"""Compute linearly interpolated percentiles without converting values to float."""
from decimal import Decimal, InvalidOperation
from typing import Iterable


def decimal_percentile(
    values: Iterable[Decimal | int | str], fraction: Decimal | int | str
) -> Decimal:
    """Return the percentile at a fraction in [0, 1] using (n - 1) rank."""
    try:
        data = [v if isinstance(v, Decimal) else Decimal(str(v)) for v in values]
        level = fraction if isinstance(fraction, Decimal) else Decimal(str(fraction))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("values and fraction must be valid decimals") from exc
    if not data:
        raise ValueError("at least one value is required")
    if any(not value.is_finite() for value in data):
        raise ValueError("values must be finite")
    if not level.is_finite() or not Decimal(0) <= level <= Decimal(1):
        raise ValueError("fraction must be finite and between zero and one")

    data.sort()
    position = level * (len(data) - 1)
    lower = int(position)
    upper = min(lower + 1, len(data) - 1)
    weight = position - lower
    return data[lower] + (data[upper] - data[lower]) * weight


if __name__ == "__main__":
    assert decimal_percentile(["0.1", "0.2", "0.4", "0.8"], "0.5") == Decimal("0.3")
    assert decimal_percentile([9, 1, 5], 0) == Decimal(1)
    assert decimal_percentile([9, 1, 5], 1) == Decimal(9)
    assert decimal_percentile([Decimal("2.5")], "0.37") == Decimal("2.5")
    for sample, level in [([], 0), ([1], "NaN"), (["Infinity"], 0), ([1], "1.1")]:
        try:
            decimal_percentile(sample, level)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid percentile input was accepted")
    print("Decimal percentile self-check passed")
