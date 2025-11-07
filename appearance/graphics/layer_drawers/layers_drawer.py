from attrs import frozen

from mathematics.vector import Vector2
import appearance.protocols as proto


@frozen
class LayersDrawer(proto.DrawableLayer):
    _layers: list[proto.Layer]

    def draw(self, mouse_position: Vector2) -> None:
        for layer in self._layers:
            layer.draw(mouse_position)
