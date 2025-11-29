from attrs import define

import appearance.protocols as proto
from appearance.UI.layouts.layout import Layout
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2


@define
class HorizontalLayout(Layout):
    def _reshape_all(self, elements: list[proto.UiElement], margin_ratio: float) -> None:
        x, y = self.rectangle.left_up_corner
        width, height = self.rectangle.shape
        total_empty = width * margin_ratio

        margin = total_empty / (len(elements) - 1) if len(elements) > 1 else 0
        element_width = (width - total_empty) / len(elements) if len(elements) else 1
        delta = margin + element_width

        for index, element in enumerate(elements):
            element.set_rectangle(
                Rectangle(Vector2(x + index * delta, y),
                          Vector2(element_width, height))
            )
