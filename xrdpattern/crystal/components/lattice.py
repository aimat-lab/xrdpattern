from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Optional

from holytools.abstract import Serializable

LatticeParams = tuple[float,float,float,float,float,float]

@dataclass(frozen=True)
class Angles(Serializable):
    alpha: Optional[float]
    beta: Optional[float]
    gamma: Optional[float]

    def as_tuple(self) -> tuple:
        return self.alpha, self.beta, self.gamma

    def to_str(self) -> str:
        s = json.dumps(asdict(self))
        return s

    @classmethod
    def from_str(cls, s: str):
        the_dict = json.loads(s)
        return cls(**the_dict)


@dataclass(frozen=True)
class Lengths(Serializable):
    a: Optional[float]
    b: Optional[float]
    c: Optional[float]

    def as_tuple(self) -> tuple:
        return self.a, self.b, self.c

    def to_str(self) -> str:
        s = json.dumps(asdict(self))
        return s

    @classmethod
    def from_str(cls, s: str):
        the_dict = json.loads(s)
        return cls(**the_dict)

    def __mul__(self, other):
        if isinstance(other, Lengths):
            return Lengths(self.a * other.a, self.b * other.b, self.c * other.c)
        elif isinstance(other, (int, float)):
            return Lengths(self.a * other, self.b * other, self.c * other)
        else:
            raise TypeError(f"Unsupported operand type(s) for *: 'Primitives' and '{type(other).__name__}'")


