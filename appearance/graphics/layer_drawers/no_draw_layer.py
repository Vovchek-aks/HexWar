from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class NoDrawLayer(proto.DrawableLayer):
    def draw(self, mouse_position: Vector2) -> None:
        ...
