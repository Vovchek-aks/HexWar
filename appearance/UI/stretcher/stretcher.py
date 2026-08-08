from typing import Iterable

from attrs import define, field

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class StretcherUi(proto.ElementUi):
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
        old_rectangle = self._rectangle
        self._rectangle = rectangle
        self._reshape_all(old_rectangle)

    def append(self, element: proto.ElementUi) -> None:
        self._elements.append(element)
        self._layer = Layer.as_multiple(self._elements)

    def extend(self, elements: Iterable[proto.ElementUi]) -> None:
        for element in elements:
            self.append(element)

    def _reshape_all(self, old_rectangle: Rectangle) -> None:
        if not self._elements:
            return

        delta = self._rectangle.position - old_rectangle.position
        ratios = Vector2(self._rectangle.shape.x / old_rectangle.shape.x,
                         self._rectangle.shape.y / old_rectangle.shape.y)

        for element in self._elements:
            rectangle = element.rectangle
            element_delta = rectangle.position - old_rectangle.position
            new_position = rectangle.position + delta - element_delta + Vector2(element_delta.x * ratios.x,
                                                                                element_delta.y * ratios.y)
            new_shape = Vector2(rectangle.shape.x * ratios.x,
                                rectangle.shape.y * ratios.y)
            element.set_rectangle(Rectangle(new_position, new_shape))
