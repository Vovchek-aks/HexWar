from abc import ABCMeta
from typing import Iterable

from attrs import define, field
from typing_extensions import ClassVar

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle


@define
class LayoutUi(proto.ElementUi, metaclass=ABCMeta):
    DEFAULT_MARGIN_RATIO: ClassVar[float] = .05

    _rectangle: Rectangle
    _margin_ratio: float = DEFAULT_MARGIN_RATIO
    _reserved: int = 0
    _layer: proto.Layer = field(init=False, factory=Layer.empty)
    _elements: list[proto.ElementUi] = field(init=False, factory=list)

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def elements_count(self) -> int:
        return max(self._reserved, len(self._elements))

    @property
    def margin_ratio(self) -> float:
        return self._margin_ratio

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._reshape(self._elements, [], self._margin_ratio)

    def append(self, element: proto.ElementUi) -> None:
        self._elements.append(element)
        self._layer = Layer.as_multiple(self._elements)
        not_to_reshape = list(range(len(self._elements) - 1)) if self._reserved >= len(self._elements) else []
        self._reshape(self._elements, not_to_reshape, self._margin_ratio)

    def extend(self, elements: Iterable[proto.ElementUi]) -> None:
        for element in elements:
            self.append(element)

    def clear(self) -> None:
        self._elements.clear()
        self._layer = Layer.as_multiple([])

    def _reshape(self,
                 elements: list[proto.ElementUi],
                 not_to_reshape: list[int],
                 margin_ratio: float) -> None:
        ...

    def __len__(self) -> int:
        return self.elements_count
