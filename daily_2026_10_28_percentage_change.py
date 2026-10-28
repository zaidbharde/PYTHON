"""Calculate percentage change while handling a zero baseline explicitly."""
def percentage_change(old: float, new: float) -> float | None:
    """Return percent change, or None when change from zero is undefined."""
    if old == 0:
        return 0.0 if new == 0 else None
    return (new - old) / abs(old) * 100
if __name__ == "__main__":
    assert percentage_change(100, 125) == 25
    assert percentage_change(0, 4) is None
    print("percentage change checks passed")
