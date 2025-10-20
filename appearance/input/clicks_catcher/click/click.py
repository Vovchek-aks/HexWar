from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class Click(proto.Click):
    _screen_position: Vector2

    _is_left: bool
    _is_right: bool
    _is_middle: bool

    @property
    def screen_position(self) -> Vector2:
        return self._screen_position

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def is_right(self) -> bool:
        return self._is_right

    @property
    def is_middle(self) -> bool:
        return self._is_middle
