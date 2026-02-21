from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from color import Color
from mathematics.vector import Vector2Int


@frozen
class BackgroundDrawer(proto.BackgroundDrawer):
    _screen_shape: Vector2Int
    _color: Color

    def draw_background(self) -> None:
        rectangle = arc.rect.LBWH(*Vector2Int.zero().tuple, *self._screen_shape.tuple)
        arc.draw_rect_filled(rectangle, self._color)
