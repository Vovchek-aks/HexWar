from attrs import frozen
from .vector2 import Vector2


@frozen
class Vector2Int:
    @classmethod
    def zero(cls) -> "Vector2Int":
        return cls(0, 0)

    @classmethod
    def right(cls) -> "Vector2Int":
        return cls(1, 0)

    @classmethod
    def up(cls) -> "Vector2Int":
        return cls(0, 1)

    @classmethod
    def ones(cls) -> "Vector2Int":
        return cls(1, 1)

    @classmethod
    def from_vector2(cls, vector: Vector2, *, strict: bool = True) -> "Vector2Int":
        x = vector.x
        y = vector.y

        if strict and not (x.is_integer() and y.is_integer()):
            raise ValueError("Strict mode requires integer values.")

        return cls(int(x), int(y))

    x: int
    y: int

    @property
    def inverse(self) -> "Vector2Int":
        return self * -1

    @property
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** .5

    @property
    def tuple(self) -> tuple[int, int]:
        return self.x, self.y

    @property
    def as_vector2(self) -> Vector2:
        return Vector2(*self.tuple)

    def scale_rounded(self, ratio: float) -> "Vector2Int":
        return type(self).from_vector2(self.as_vector2 * ratio, strict=False)

    def with_x(self, x: int) -> "Vector2Int":
        return type(self)(x, self.y)

    def with_y(self, y: int) -> "Vector2Int":
        return type(self)(self.x, y)

    def __add__(self, other: "Vector2Int") -> "Vector2Int":
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2Int") -> "Vector2Int":
        return self + -other

    def __mul__(self, number: int) -> "Vector2Int":
        return type(self)(self.x * number, self.y * number)

    def __neg__(self) -> "Vector2Int":
        return self.inverse
