from attrs import define, field
from typing import Protocol, Callable

import appearance.protocols as proto
from appearance.UI.button import ButtonUi
from appearance.UI.stretcher import StretcherUi
from appearance.UI.text import TextUi, TextData
from appearance.graphics.colors import RECTANGLE_BUTTON
from appearance.graphics.sprites import SpritesLoader
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
from observer import Event, OnEventSubscriber


@define(hash=True)
class TwoButtonsValueChanger[T](proto.ElementUi):
    @classmethod
    def make_horizontal(cls,
                        rectangle: Rectangle,
                        changer: "ValueChanger",
                        sprites_loader: SpritesLoader,
                        drawer: proto.UiDrawer,
                        *,
                        margin_ratio: float = 0,
                        get_text: Callable[[T], str] = lambda value: str(value)) -> "TwoButtonsValueChanger":
        margin = rectangle.shape.x * margin_ratio
        stretcher = StretcherUi(rectangle)

        buttons_shape = Vector2.ones() * rectangle.shape.y
        text = TextUi.make(drawer,
                           Rectangle(rectangle.position + (buttons_shape.x + margin) * Vector2.right(),
                                     rectangle.shape - 2 * (buttons_shape.x + margin) * Vector2.right()),
                           TextData.debug(get_text(changer.value)), is_center=True)

        self = TwoButtonsValueChanger(stretcher, text, changer, get_text)

        back = ButtonUi.make(drawer,
                             Rectangle(rectangle.position, buttons_shape),
                             sprites_loader.load_button_3_to_2().colored_in(RECTANGLE_BUTTON),
                             TextData.for_button("<"))
        back.was_clicked.subscribe(self.back)

        next_ = ButtonUi.make(drawer,
                              Rectangle(rectangle.position + Vector2(rectangle.shape.x - buttons_shape.x, 0),
                                        buttons_shape),
                              sprites_loader.load_button_3_to_2().colored_in(RECTANGLE_BUTTON),
                              TextData.for_button(">"))
        next_.was_clicked.subscribe(self.next)

        stretcher.extend([back, text, next_])

        return self

    _stretcher: StretcherUi = field(hash=False)
    _text: TextUi = field(hash=False)
    _changer: "ValueChanger[T]" = field(hash=False)
    _get_text: Callable[[T], str] = field(hash=False)

    _value_had_changed: Event[T, None] = field(init=False, factory=Event, hash=False)

    _id = field(init=False, hash=True)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

    @property
    def value(self) -> T:
        return self._changer.value

    @property
    def changer(self) -> "ValueChanger[T]":
        return self._changer

    @property
    def rectangle(self) -> Rectangle:
        return self._stretcher.rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._stretcher.layer

    @property
    def text(self) -> TextUi:
        return self._text

    @property
    def value_had_changed(self) -> OnEventSubscriber[T, None]:
        return self._value_had_changed.subscriber

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._stretcher.set_rectangle(rectangle)

    def set(self, value: T) -> None:
        self._changer.set(value)
        self._update_text()
        self._value_had_changed.invoke(self.value)

    def next(self) -> None:
        self._changer.next()
        self._update_text()
        self._value_had_changed.invoke(self.value)

    def back(self) -> None:
        self._changer.back()
        self._update_text()
        self._value_had_changed.invoke(self.value)

    def _update_text(self) -> None:
        self._text.set_text(self._get_text(self._changer.value))


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
