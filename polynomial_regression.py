def fit_polynomial(x_vals, y_vals, degree):
    n = degree + 1
    A = [[sum(x**(i + j) for x in x_vals) for j in range(n)] for i in range(n)]
    b = [sum(y_vals[k] * x_vals[k]**i for k in range(len(x_vals))) for i in range(n)]

    for i in range(n):
        pivot = A[i][i]
        for j in range(n):
            A[i][j] /= pivot
        b[i] /= pivot
        for k in range(n):
            if k != i:
                factor = A[k][i]
                for j in range(n):
                    A[k][j] -= factor * A[i][j]
                b[k] -= factor * b[i]
    return b


def evaluate(coeffs, x):
    return sum(c * x**i for i, c in enumerate(coeffs))


if __name__ == "__main__":
    x_vals = [0, 1, 2, 3, 4]
    y_vals = [1, 3, 7, 13, 21]
    coeffs = fit_polynomial(x_vals, y_vals, 2)
    print("Coefficients:", [round(c, 3) for c in coeffs])
    for x in x_vals:
        print(f"f({x}) = {evaluate(coeffs, x):.2f}, actual = {y_vals[x]}")
