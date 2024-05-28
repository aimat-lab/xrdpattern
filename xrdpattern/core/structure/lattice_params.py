from __future__ import annotations

from dataclasses import dataclass

from holytools.abstract import JsonDataclass

LatticeParams = tuple[float,float,float,float,float,float]

@dataclass(frozen=True)
class Angles(JsonDataclass):
    alpha: float
    beta: float
    gamma: float

    @classmethod
    def make_example(cls) -> Angles:
        return cls(alpha=90, beta=90, gamma=90)

    def __iter__(self):
        return iter((self.alpha, self.beta, self.gamma))

    def as_tuple(self) -> tuple:
        return self.alpha, self.beta, self.gamma


@dataclass(frozen=True)
class Lengths(JsonDataclass):
    a: float
    b: float
    c: float

    def __hash__(self):
        return id(self)

    @classmethod
    def make_example(cls) -> Lengths:
        return cls(a=3, b=3, c=3)

    def __iter__(self):
        return iter((self.a, self.b, self.c))

    def as_tuple(self) -> tuple:
        return self.a, self.b, self.c

    def __mul__(self, other):
        if isinstance(other, Lengths):
            return Lengths(self.a * other.a, self.b * other.b, self.c * other.c)
        elif isinstance(other, (int, float)):
            return Lengths(self.a * other, self.b * other, self.c * other)
        else:
            raise TypeError(f"Unsupported operand type(s) for *: 'Primitives' and '{type(other).__name__}'")


