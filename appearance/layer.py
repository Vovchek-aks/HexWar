from attrs import frozen

import appearance.protocols as proto
from mathematics.vector import Vector2


@frozen
class Layer(proto.DrawableLayer, proto.ClicksCatchingLayer):
    _drawable_layer: proto.DrawableLayer
    _clicks_catching_layer: proto.ClicksCatchingLayer

    @property
    def drawable_layer(self) -> proto.DrawableLayer:
        return self._drawable_layer

    @property
    def clicks_catching_layer(self) -> proto.ClicksCatchingLayer:
        return self._clicks_catching_layer

    def draw(self, mouse_position: Vector2) -> None:
        self._drawable_layer.draw(mouse_position)

    def can_catch(self, click: proto.Click) -> bool:
        return self._clicks_catching_layer.can_catch(click)

    def catch(self, click: proto.Click) -> None:
        self._clicks_catching_layer.catch(click)
