from attrs import frozen


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

    x: int
    y: int

    @property
    def tuple(self) -> tuple[int, int]:
        return self.x, self.y

    def with_x(self, x: int) -> "Vector2Int":
        return type(self)(x, self.y)

    def with_y(self, y: int) -> "Vector2Int":
        return type(self)(self.x, y)

    def __add__(self, other: "Vector2Int") -> "Vector2Int":
        return type(self)(self.x + other.x, self.y + other.y)

    def __mul__(self, number: int) -> "Vector2Int":
        return type(self)(self.x * number, self.y * number)
