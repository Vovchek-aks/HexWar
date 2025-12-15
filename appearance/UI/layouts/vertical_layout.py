from attrs import define

import appearance.protocols as proto
from appearance.UI.layouts.layout import LayoutUi
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class VerticalLayoutUi(LayoutUi):
    def _reshape_all(self, elements: list[proto.ElementUi], margin_ratio: float) -> None:
        x, y = self.rectangle.position
        width, height = self.rectangle.shape
        total_empty = height * margin_ratio

        margin = total_empty / (len(elements) - 1) if len(elements) > 1 else 0
        element_height = (height - total_empty) / len(elements) if len(elements) else 1
        delta = margin + element_height

        for index, element in enumerate(elements):
            element.set_rectangle(
                Rectangle(Vector2(x, y + index * delta),
                          Vector2(width, element_height))
            )
