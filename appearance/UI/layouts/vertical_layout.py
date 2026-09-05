from attrs import define, field

import appearance.protocols as proto
from appearance.UI.layouts.layout import LayoutUi
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define(hash=True)
class VerticalLayoutUi(LayoutUi):
    _id = field(init=False, hash=True)

    def __attrs_post_init__(self) -> None:
        self._id = id(self)

    def _reshape(self,
                 elements: list[proto.ElementUi],
                 weight_of: dict[proto.ElementUi, float],
                 not_to_reshape: list[int],
                 margin_ratio: float) -> None:
        x, y = self.rectangle.position
        width, height = self.rectangle.shape
        total_empty = height * margin_ratio if self.elements_count > 1 else 0

        margin = total_empty / (self.elements_count - 1) if self.elements_count > 1 else 0
        base_element_height = (height - total_empty) / (sum(weight_of.values()) + self.elements_count - len(weight_of)
                                                        if self.elements_count else 1)
        delta = y + height
        for index, element in enumerate(elements):
            element_height = base_element_height * weight_of[element]
            element_y = delta - element_height
            delta -= element_height + margin

            if index in not_to_reshape:
                continue

            element.set_rectangle(
                Rectangle(Vector2(x, element_y),
                          Vector2(width, element_height))
            )
