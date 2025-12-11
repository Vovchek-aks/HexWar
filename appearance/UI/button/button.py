from attrs import define, field

import appearance.protocols as proto
from appearance.UI.image import ImageUi
from appearance.UI.text import TextUi
from appearance.graphics.sprites import Sprite
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from observer import Event, OnEventSubscriber

MARGIN = Vector2(10, 10)


@define
class ButtonUi(proto.UiElement):
    @classmethod
    def make(cls,
             drawer: proto.UiDrawer,
             rectangle: Rectangle,
             sprite: Sprite,
             text_data: proto.TextData) -> "ButtonUi":
        image = ImageUi.make(drawer, rectangle, sprite)
        text = TextUi.make(drawer, get_text_rectangle(rectangle), text_data)

        layers = [
            text,
            image
        ]

        self = cls(image.rectangle, Layer.as_multiple(layers), text, image)
        self.layer.was_clicked.subscribe(self._on_layer_was_clicked)

        return self

    _was_clicked: Event[None] = field(init=False, factory=Event)

    _rectangle: Rectangle
    _layer: proto.Layer
    _text: TextUi
    _image: ImageUi

    @property
    def was_clicked(self) -> OnEventSubscriber[None]:
        return self._was_clicked.subscriber

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def image(self) -> ImageUi:
        return self._image

    @property
    def text(self) -> TextUi:
        return self._text

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._image.set_rectangle(rectangle)
        self._text.set_rectangle(get_text_rectangle(rectangle))
        ...

    def _on_layer_was_clicked(self, _: proto.Click) -> None:
        self._was_clicked.invoke()


def get_text_rectangle(rectangle: Rectangle) -> Rectangle:
    return Rectangle(rectangle.position + MARGIN, rectangle.shape - MARGIN * 2)


def get_image_rectangle(rectangle: Rectangle) -> Rectangle:
    return Rectangle(rectangle.position - MARGIN, rectangle.shape + MARGIN * 2)
