from attrs import define, field

import appearance.protocols as proto
from appearance.UI.box import BoxUi
from mathematics.rectangle import Rectangle
from .button import ButtonUi


@define(hash=True)
class SwitchButtonUi(proto.ElementUi):
    @classmethod
    def make(cls, rectangle: Rectangle, *buttons: ButtonUi) -> "SwitchButtonUi":
        box = BoxUi(rectangle)
        box.extend(buttons)

        self = SwitchButtonUi(box, list(buttons))
        for button in buttons:
            button.layer.set_activity(False)

        self.button.layer.set_activity(True)
        return self

    _box: BoxUi = field(hash=False)
    _buttons: list[ButtonUi] = field(hash=False)
    _index: int = field(hash=False, default=0)
    _id = field(init=False, hash=True)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

    @property
    def button(self) -> ButtonUi:
        return self._buttons[self._index]

    @property
    def buttons(self) -> list[ButtonUi]:
        return list(self._buttons)

    @property
    def rectangle(self) -> Rectangle:
        return self._box.rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._box.layer

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._box.set_rectangle(rectangle)

    def next(self) -> None:
        self._move(1)

    def back(self) -> None:
        self._move(-1)

    def _move(self, delta: int) -> None:
        self.button.layer.set_activity(False)
        self._index += delta
        self._index %= len(self._buttons)
        self.button.layer.set_activity(True)
