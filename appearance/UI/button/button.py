from attrs import frozen

import appearance.protocols as proto
from appearance.UI.image import ImageUi
from appearance.UI.text import TextUi
from appearance.graphics.sprites import Sprite
from appearance.layer import Layer
from mathematics.vector import Vector2


@frozen
class ButtonUi(proto.LayerHolder):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, sprite: Sprite, text: proto.TextData, position: Vector2) -> "ButtonUi":
        layers = [
            TextUi(drawer, text, position),
            ImageUi(drawer, sprite, position)
        ]
        return cls(Layer.as_multiple(layers))

    _layer: proto.Layer

    @property
    def layer(self) -> proto.Layer:
        return self._layer
