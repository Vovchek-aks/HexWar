from attrs import define, field

import appearance.protocols as proto
from appearance.UI.layouts.layout import LayoutUi
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define(hash=True)
class HorizontalLayoutUi(LayoutUi):
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
        total_empty = width * margin_ratio if self.elements_count > 1 else 0

        margin = total_empty / (self.elements_count - 1) if self.elements_count > 1 else 0
        base_element_width = (width - total_empty) / (sum(weight_of.values()) + self.elements_count - len(weight_of)
                                                      if self.elements_count else 1)
        delta = 0
        for index, element in enumerate(elements):
            element_width = base_element_width * weight_of[element]
            element_x = x + delta
            delta += element_width + margin

            if index in not_to_reshape:
                continue

            element.set_rectangle(
                Rectangle(Vector2(element_x, y),
                          Vector2(element_width, height))
            )
