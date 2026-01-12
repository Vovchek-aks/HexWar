import pygame as pg


class Vector2(pg.Vector2):
    @classmethod
    def zero(cls) -> "Vector2":
        return cls(0, 0)

    @classmethod
    def right(cls) -> "Vector2":
        return cls(1, 0)

    @classmethod
    def up(cls) -> "Vector2":
        return cls(0, 1)

    @classmethod
    def ones(cls) -> "Vector2":
        return cls(1, 1)

    @property
    def tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def with_x(self, x: float) -> "Vector2":
        return type(self)(x, self.y)

    def with_y(self, y: float) -> "Vector2":
        return type(self)(self.x, y)

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    def __repr__(self) -> str:
        return str(self)
