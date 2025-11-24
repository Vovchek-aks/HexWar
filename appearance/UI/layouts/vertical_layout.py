from attrs import define, field

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class VerticalLayout(proto.UiElement):
    _rectangle: Rectangle
    _margin_ratio: float = .1
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
        self._reshape_all()

    def append(self, element: proto.UiElement) -> None:
        self._elements.append(element)
        self._layer = Layer.as_multiple(self._elements)
        self._reshape_all()

    def _reshape_all(self) -> None:
        x, y = self._rectangle.left_up_corner
        width, height = self._rectangle.shape
        total_empty = height * self._margin_ratio

        margin = total_empty / (len(self._elements) - 1) if len(self._elements) > 1 else 0
        element_height = (height - total_empty) / len(self._elements)
        delta = margin + element_height

        for index, element in enumerate(self._elements):
            element.set_rectangle(
                Rectangle(Vector2(x, y + index * delta),
                          Vector2(width, element_height))
            )
