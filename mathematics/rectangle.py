from attrs import frozen

from mathematics.vector import Vector2


@frozen
class Rectangle:
    @classmethod
    def zero(cls) -> "Rectangle":
        return cls(Vector2.zero(), Vector2.zero())

    @classmethod
    def with_center_at(cls, center: Vector2, shape: Vector2) -> "Rectangle":
        position = center - shape / 2
        return cls(position, shape)

    _position: Vector2
    _shape: Vector2

    @property
    def shape(self) -> Vector2:
        return self._shape

    @property
    def left_right_up_bottom(self) -> tuple[float, float, float, float]:
        left = self._position.x
        up = self._position.y
        right = left + self._shape.x
        bottom = up + self._shape.y
        return left, right, up, bottom

    @property
    def center(self) -> Vector2:
        return self._position + self._shape / 2

    @property
    def left_up_corner(self) -> Vector2:
        return Vector2(self._position)

    def is_surrounding(self, point: Vector2) -> bool:
        left, right, up, bottom = self.left_right_up_bottom

        return (left <= point.x <= right and
                up <= point.y <= bottom)
