from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Parser:
    source: str
    position: int = 0

    def parse(self) -> float:
        value = self._expression()
        self._spaces()
        if self.position != len(self.source):
            raise ValueError(f"unexpected input at {self.position}")
        return value

    def _expression(self) -> float:
        value = self._term()
        while True:
            self._spaces()
            if self._take("+"):
                value += self._term()
            elif self._take("-"):
                value -= self._term()
            else:
                return value

    def _term(self) -> float:
        value = self._factor()
        while True:
            self._spaces()
            if self._take("*"):
                value *= self._factor()
            elif self._take("/"):
                divisor = self._factor()
                if divisor == 0:
                    raise ZeroDivisionError("division by zero")
                value /= divisor
            else:
                return value

    def _factor(self) -> float:
        self._spaces()
        if self._take("("):
            value = self._expression()
            self._spaces()
            if not self._take(")"):
                raise ValueError("missing closing parenthesis")
            return value
        start = self.position
        while self.position < len(self.source) and (self.source[self.position].isdigit() or self.source[self.position] == "."):
            self.position += 1
        if start == self.position:
            raise ValueError(f"number expected at {self.position}")
        return float(self.source[start:self.position])

    def _spaces(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def _take(self, token: str) -> bool:
        if self.source.startswith(token, self.position):
            self.position += len(token)
            return True
        return False


if __name__ == "__main__":
    print(Parser("(12 + 8) / 5 * 3").parse())
