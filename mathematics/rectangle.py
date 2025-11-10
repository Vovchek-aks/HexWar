from attrs import frozen

from mathematics.vector import Vector2


@frozen
class Rectangle:
    _position: Vector2
    _shape: Vector2

    @property
    def left_right_up_bottom(self) -> tuple[float, float, float, float]:
        left = self._position.x
        up = self._position.y
        right = left + self._shape.x
        bottom = up + self._shape.y
        return left, right, up, bottom

    def is_surrounding(self, point: Vector2) -> bool:
        left, right, up, bottom = self.left_right_up_bottom

        return (left <= point.x <= right and
                up <= point.y <= bottom)
