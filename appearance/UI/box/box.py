from typing import Iterable

from attrs import define, field

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle


@define
class BoxUi(proto.ElementUi):
    _rectangle: Rectangle
    _layer: proto.Layer = field(init=False, factory=Layer.empty)
    _elements: list[proto.ElementUi] = field(init=False, factory=list)

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._reshape_all()

    def append(self, element: proto.ElementUi) -> None:
        element.set_rectangle(self.rectangle)
        self._elements.append(element)
        self._layer = Layer.as_multiple(self._elements)

    def extend(self, elements: Iterable[proto.ElementUi]) -> None:
        for element in elements:
            self.append(element)

    def _reshape_all(self) -> None:
        for element in self._elements:
            element.set_rectangle(self.rectangle)
