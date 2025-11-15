from attrs import frozen, field

import appearance.protocols as proto
from appearance.UI.image import ImageUi
from appearance.UI.text import TextUi
from appearance.graphics.sprites import Sprite
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int
from observer import Event, OnEventSubscriber

MARGIN = Vector2Int(10, 10)


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

        self = cls(image.rectangle, Layer.as_multiple(layers))
        self.layer.was_clicked.subscribe(self._on_layer_was_clicked)

        return self

    _was_clicked: Event[None] = field(init=False, factory=Event)

    _rectangle: Rectangle
    _layer: proto.Layer

    @property
    def was_clicked(self) -> OnEventSubscriber[None]:
        return self._was_clicked.subscriber

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    def _on_layer_was_clicked(self, _: proto.Click) -> None:
        self._was_clicked.invoke()
