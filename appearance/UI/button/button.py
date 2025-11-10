from attrs import frozen, field

import appearance.protocols as proto
from appearance.UI.image import ImageUi
from appearance.UI.text import TextUi
from appearance.graphics.sprites import Sprite
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@frozen
class ButtonUi(proto.UiElement):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, sprite: Sprite, text_data: proto.TextData, position: Vector2) -> "ButtonUi":
        image = ImageUi(drawer, sprite, position)
        text = TextUi(drawer, text_data, position)

        layers = [
            text,
            image
        ]
        return cls(image.rectangle, Layer.as_multiple(layers))

    _rectangle: Rectangle
    _layer: proto.Layer

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle
