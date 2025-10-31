from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class Buttons:
    _is_left: bool = False
    _is_right: bool = False
    _is_middle: bool = False

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def is_right(self) -> bool:
        return self._is_right

    @property
    def is_middle(self) -> bool:
        return self._is_middle


@frozen
class Click(proto.Click):
    _screen_position: Vector2
    _buttons: Buttons

    @property
    def screen_position(self) -> Vector2:
        return self._screen_position

    @property
    def is_left(self) -> bool:
        return self._buttons.is_left

    @property
    def is_right(self) -> bool:
        return self._buttons.is_right

    @property
    def is_middle(self) -> bool:
        return self._buttons.is_middle
