from attrs import frozen

import appearance.protocols as proto
from appearance.UI.image import ImageUi
from appearance.UI.text import TextUi
from appearance.graphics.sprites import Sprite
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int

MARGIN = Vector2Int(40, 10)


@frozen
class ButtonUi(proto.UiElement):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, position: Vector2, sprite: Sprite, text_data: proto.TextData) -> "ButtonUi":
        sprite = sprite.reshape(Vector2Int.from_vector2(text_data.shape) + MARGIN * 2)
        image = ImageUi.make(drawer, position, sprite)
        text = TextUi.make(drawer, position, text_data)

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
