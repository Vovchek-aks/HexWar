from typing import Iterable

from attrs import frozen

from mathematics.vector import Vector2
import appearance.protocols as proto


@frozen
class LayersDrawer(proto.DrawableLayer):
    _layers: list[proto.LayerHolder]

    def draw(self, mouse_position: Vector2) -> None:
        for layer in self._get_active_layers():
            layer.draw(mouse_position)

    def _get_active_layers(self) -> Iterable[proto.Layer]:
        return (layer.layer for layer in self._layers if layer.layer.is_active)
