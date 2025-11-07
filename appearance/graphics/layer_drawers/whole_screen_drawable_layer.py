from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class WholeScreenDrawableLayer(proto.DrawableLayer):
    _draw: proto.Draw

    def draw(self, mouse_position: Vector2) -> None:
        self._draw.background()
