def lcs_diff(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    diff = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            diff.append(("equal", a[i - 1]))
            i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            diff.append(("removed", a[i - 1]))
            i -= 1
        else:
            diff.append(("added", b[j - 1]))
            j -= 1
    while i > 0:
        diff.append(("removed", a[i - 1])); i -= 1
    while j > 0:
        diff.append(("added", b[j - 1])); j -= 1

    return diff[::-1]


if __name__ == "__main__":
    old_lines = ["hello", "world", "foo"]
    new_lines = ["hello", "there", "foo", "bar"]
    for op, line in lcs_diff(old_lines, new_lines):
        prefix = {"equal": " ", "removed": "-", "added": "+"}[op]
        print(f"{prefix} {line}")
