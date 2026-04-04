from attrs import frozen
from typing import Protocol

import appearance.protocols as proto
from appearance.UI.button import ButtonUi
from appearance.UI.stretcher import StretcherUi
from appearance.UI.text import TextUi, TextData
from appearance.graphics.sprites import SpritesLoader
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@frozen
class TwoButtonsValueChanger[T](proto.ElementUi):
    @classmethod
    def make_horizontal(cls,
                        rectangle: Rectangle,
                        changer: "ValueChanger",
                        sprites_loader: SpritesLoader,
                        drawer: proto.UiDrawer) -> "TwoButtonsValueChanger":
        stretcher = StretcherUi(rectangle)

        buttons_shape = Vector2.ones() * rectangle.shape.y
        text = TextUi.make(drawer,
                           Rectangle(rectangle.position + buttons_shape.x * Vector2.right(),
                                     rectangle.shape - 2 * buttons_shape.x * Vector2.right()),
                           TextData.debug(str(changer.value)), is_center=True)

        self = TwoButtonsValueChanger(stretcher, text, changer)

        back = ButtonUi.make_null("<", self.back, sprites_loader, drawer)
        back.set_rectangle(Rectangle(rectangle.position, buttons_shape))

        next_ = ButtonUi.make_null(">", self.next, sprites_loader, drawer)
        next_.set_rectangle(Rectangle(rectangle.position + Vector2(rectangle.shape.x - buttons_shape.x, 0),
                                      buttons_shape))

        stretcher.extend([back, text, next_])

        return self

    _stretcher: StretcherUi
    _text: TextUi
    _changer: "ValueChanger[T]"

    @property
    def value(self) -> T:
        return self._changer.value

    @property
    def rectangle(self) -> Rectangle:
        return self._stretcher.rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._stretcher.layer

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._stretcher.set_rectangle(rectangle)

    def set(self, value: T) -> None:
        self._changer.set(value)
        self._update_text()

    def next(self) -> None:
        self._changer.next()
        self._update_text()

    def back(self) -> None:
        self._changer.back()
        self._update_text()

    def _update_text(self) -> None:
        self._text.set_text(str(self._changer.value))


class ValueChanger[T](Protocol):
    @property
    def value(self) -> T:
        ...

    def set(self, value: T) -> None:
        ...

    def next(self) -> None:
        ...

    def back(self) -> None:
        ...
