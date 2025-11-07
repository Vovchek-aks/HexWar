from typing import Callable

from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class FunctionLayerDrawer(proto.DrawableLayer):
    _draw: Callable[[Vector2], None]

    def draw(self, mouse_position: Vector2) -> None:
        self._draw(mouse_position)
