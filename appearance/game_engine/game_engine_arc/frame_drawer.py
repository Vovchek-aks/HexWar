from attrs import frozen

from appearance.graphics.layer_drawers.layers_drawer import LayersDrawer
from appearance.layer import Layer
from mathematics.vector import Vector2
import appearance.protocols as proto


@frozen
class FrameDrawer(proto.FrameDrawer):
    @classmethod
    def make(cls, layers: list[Layer]) -> "FrameDrawer":
        return cls(LayersDrawer(layers[::-1]))

    _layers: LayersDrawer

    def draw_frame(self, mouse_position: Vector2) -> None:
        self._layers.draw(mouse_position)
