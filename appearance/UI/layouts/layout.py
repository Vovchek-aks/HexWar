from abc import ABCMeta

from attrs import define, field

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle


@define
class Layout(proto.UiElement, metaclass=ABCMeta):
    _rectangle: Rectangle
    _margin_ratio: float = .05
    _layer: proto.Layer = field(init=False, factory=Layer.empty)
    _elements: list[proto.UiElement] = field(init=False, factory=list)

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._reshape_all(self._elements, self._margin_ratio)

    def append(self, element: proto.UiElement) -> None:
        self._elements.append(element)
        self._layer = Layer.as_multiple(self._elements)
        self._reshape_all(self._elements, self._margin_ratio)

    def _reshape_all(self, elements: list[proto.UiElement], margin_ratio: float) -> None:
        ...
