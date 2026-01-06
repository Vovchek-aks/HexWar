from attrs import frozen
import arcade as arc

from appearance.graphics.colors import BACKGROUND
import appearance.protocols as proto
from mathematics.vector import Vector2Int


@frozen
class BackgroundDrawer(proto.BackgroundDrawer):
    _screen_shape: Vector2Int

    def draw_background(self) -> None:
        rectangle = arc.rect.LBWH(*Vector2Int.zero().tuple, *self._screen_shape.tuple)
        arc.draw_rect_filled(rectangle, BACKGROUND)
