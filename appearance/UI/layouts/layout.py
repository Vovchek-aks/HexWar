from abc import ABCMeta
from typing import Iterable

from attrs import define, field
from typing_extensions import ClassVar

import appearance.protocols as proto
from appearance.layer import Layer
from mathematics.rectangle import Rectangle


@define(hash=True)
class LayoutUi(proto.ElementUi, metaclass=ABCMeta):
    DEFAULT_MARGIN_RATIO: ClassVar[float] = .05

    _rectangle: Rectangle = field(hash=False)
    _margin_ratio: float = field(default=DEFAULT_MARGIN_RATIO, hash=False)
    _reserved: int = field(default=0, hash=False)
    _layer: proto.Layer = field(init=False, factory=Layer.empty, hash=False)
    _elements: list[proto.ElementUi] = field(init=False, factory=list, hash=False)
    _weight_of: dict[proto.ElementUi, float] = field(init=False, factory=dict, hash=False)
    _id = field(init=False, hash=True)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

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
        self._reshape(self._elements, self._weight_of, [], self._margin_ratio)

    def append(self, element: proto.ElementUi, *, weight: float = 1) -> None:
        self._elements.append(element)
        self._weight_of[element] = weight
        self._layer = Layer.as_multiple(self._elements)
        not_to_reshape = list(range(len(self._elements) - 1)) if self._reserved >= len(self._elements) else []
        self._reshape(self._elements, self._weight_of, not_to_reshape, self._margin_ratio)

    def extend(self, elements: Iterable[proto.ElementUi]) -> None:
        for element in elements:
            self.append(element)

    def clear(self) -> None:
        self._elements.clear()
        self._layer = Layer.as_multiple([])

    def _reshape(self,
                 elements: list[proto.ElementUi],
                 weight_of: dict[proto.ElementUi, float],
                 not_to_reshape: list[int],
                 margin_ratio: float) -> None:
        ...

    def __len__(self) -> int:
        return self.elements_count
