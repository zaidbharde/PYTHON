class Matrix:
    def __init__(self, data):
        self.data = [row[:] for row in data]
        self.rows = len(data)
        self.cols = len(data[0])

    def __add__(self, other):
        return Matrix([[self.data[i][j] + other.data[i][j]
                        for j in range(self.cols)] for i in range(self.rows)])

    def __sub__(self, other):
        return Matrix([[self.data[i][j] - other.data[i][j]
                        for j in range(self.cols)] for i in range(self.rows)])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Matrix([[self.data[i][j] * other
                            for j in range(self.cols)] for i in range(self.rows)])
        result = [[0] * other.cols for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(self.cols):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix(result)

    def transpose(self):
        return Matrix([[self.data[j][i] for j in range(self.rows)]
                        for i in range(self.cols)])

    def determinant(self):
        if self.rows != self.cols:
            raise ValueError("Must be square")
        if self.rows == 1: return self.data[0][0]
        if self.rows == 2:
            return self.data[0][0]*self.data[1][1] - self.data[0][1]*self.data[1][0]
        det = 0
        for j in range(self.cols):
            minor = Matrix([[self.data[r][c] for c in range(self.cols) if c != j]
                            for r in range(1, self.rows)])
            det += ((-1) ** j) * self.data[0][j] * minor.determinant()
        return det

    def __repr__(self):
        lines = []
        for row in self.data:
            lines.append("  │ " + "  ".join(f"{v:>6.2f}" for v in row) + " │")
        return "\n".join(lines)


if __name__ == "__main__":
    A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B = Matrix([[9, 8, 7], [6, 5, 4], [3, 2, 1]])

    print("=" * 40)
    print("  Matrix Operations")
    print("=" * 40)

    for label, result in [
        ("A", A), ("B", B), ("A + B", A + B),
        ("A - B", A - B), ("A * B", A * B),
        ("A * 2", A * 2), ("A^T", A.transpose()),
    ]:
        print(f"\n  {label}:")
        print(result)

    C = Matrix([[6, 1, 1], [4, -2, 5], [2, 8, 7]])
    print(f"\n  det(C) = {C.determinant()}")
