from attrs import define

import appearance.protocols as proto
from appearance.UI.box import BoxUi
from mathematics.rectangle import Rectangle
from .button import ButtonUi


@define
class SwitchButtonUI(proto.ElementUi):
    @classmethod
    def make(cls, rectangle: Rectangle, *buttons: ButtonUi) -> "SwitchButtonUI":
        box = BoxUi(rectangle)
        box.extend(buttons)

        self = SwitchButtonUI(box, list(buttons))
        for button in buttons:
            button.layer.set_activity(False)

        self.button.layer.set_activity(True)
        return self

    _box: BoxUi
    _buttons: list[ButtonUi]
    _index: int = 0

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
        self.button.layer.set_activity(False)
        self._index += 1
        self._index %= len(self._buttons)
        self.button.layer.set_activity(True)
