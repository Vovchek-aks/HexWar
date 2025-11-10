from attrs import frozen

from mathematics.vector import Vector2
import appearance.protocols as proto


@frozen
class LayersDrawer(proto.DrawableLayer):
    _layers: list[proto.LayerHolder]

    def draw(self, mouse_position: Vector2) -> None:
        for layer_holder in self._layers:
            layer_holder.layer.draw(mouse_position)
