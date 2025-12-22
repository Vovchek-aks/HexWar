from attrs import frozen, define, field

from mathematics.vector import Vector2, Vector2Int
from statuses import Status, MISSING


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
    def position(self) -> Vector2:
        return Vector2(self._position)

    def is_surrounding(self, point: Vector2) -> bool:
        left, right, up, bottom = self.left_right_up_bottom

        return (left <= point.x <= right and
                up <= point.y <= bottom)


@define
class RectangleBuilder:
    _screen_shape: Vector2Int = field()

    _coordinates_multiplier = field(init=False, default=Vector2Int(1, 1))
    _position: Vector2 = field(init=False, factory=Vector2.zero)
    _shape: Vector2 | Status = field(init=False, default=MISSING)

    def is_valid(self) -> bool:
        return MISSING not in (self._position, self._shape)

    def build(self) -> Rectangle:
        assert self.is_valid()
        return Rectangle(self._position, self._shape)

    def set_shape(self, shape: Vector2) -> "RectangleBuilder":
        self._shape = shape
        return self

    def move(self, position: Vector2) -> "RectangleBuilder":
        self._position += Vector2(position.x * self._coordinates_multiplier.x,
                                  position.y * self._coordinates_multiplier.y)
        return self

    def adjust_for_shape(self) -> "RectangleBuilder":
        return self.move(Vector2(self._shape.x if self._coordinates_multiplier.x < 0 else 0,
                                 self._shape.y if self._coordinates_multiplier.y < 0 else 0))

    def from_left_up(self) -> "RectangleBuilder":
        self._position = Vector2.zero()
        self._coordinates_multiplier = Vector2Int(1, 1)
        return self

    def from_left_bottom(self) -> "RectangleBuilder":
        self._position = self._screen_shape.with_x(0).as_vector2
        self._coordinates_multiplier = Vector2Int(1, -1)
        return self

    def from_right_bottom(self) -> "RectangleBuilder":
        self._position = self._screen_shape.as_vector2
        self._coordinates_multiplier = Vector2Int(-1, -1)
        return self

    def from_right_up(self) -> "RectangleBuilder":
        self._position = self._screen_shape.with_y(0).as_vector2
        self._coordinates_multiplier = Vector2Int(-1, 1)
        return self
