from attrs import frozen

import appearance.protocols as proto
from .mouse_buttons import MouseButtons
from mathematics.vector import Vector2


@frozen
class Click(proto.Click):
    _screen_position: Vector2
    _buttons: MouseButtons

    @property
    def screen_position(self) -> Vector2:
        return self._screen_position

    @property
    def buttons(self) -> MouseButtons:
        return self._buttons
