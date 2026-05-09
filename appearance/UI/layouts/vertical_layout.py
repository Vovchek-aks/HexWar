from attrs import define

import appearance.protocols as proto
from appearance.UI.layouts.layout import LayoutUi
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class VerticalLayoutUi(LayoutUi):
    def _reshape(self,
                 elements: list[proto.ElementUi],
                 not_to_reshape: list[int],
                 margin_ratio: float) -> None:
        x, y = self.rectangle.position
        width, height = self.rectangle.shape
        total_empty = height * margin_ratio if self.elements_count > 1 else 0

        margin = total_empty / (self.elements_count - 1) if self.elements_count > 1 else 0
        element_height = (height - total_empty) / self.elements_count if self.elements_count else 1
        delta = margin + element_height

        for index, element in enumerate(elements):
            if index in not_to_reshape:
                continue

            index = self.elements_count - 1 - index
            rectangle = Rectangle(Vector2(x, y + index * delta),
                                  Vector2(width, element_height))
            element.set_rectangle(rectangle)
