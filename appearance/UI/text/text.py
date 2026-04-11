import arcade as arc
from attrs import define, field

from appearance.layer import LayerBuilder
from color import Color
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2
import appearance.protocols as proto
from observer import Event, OnEventSubscriber

HEIGHT_TO_WIDTH_RATIO = 1.45


@define
class TextUi(proto.ElementUi):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, rectangle: Rectangle, data: proto.TextData, *, is_center=False) -> "TextUi":
        text = arc.Text(data.text, *rectangle.position, color=data.color, font_size=data.font.size,
                        font_name=data.font.name, bold=data.font.is_bold, italic=data.font.is_italic)
        if is_center:
            text.anchor_x = 'center'
            text.anchor_y = 'center'

        self = cls(drawer, text, is_center, rectangle)
        self.set_rectangle(rectangle)

        layer = (LayerBuilder()
                 .not_catching()
                 .set_draw_function(self._draw)
                 .build())

        self._layer = layer
        return self

    _drawer: proto.UiDrawer
    _text: arc.Text
    _is_center: bool
    _rectangle: Rectangle
    _layer: proto.Layer = field(init=False)

    _size_was_changed: Event["TextUi", None] = field(init=False, factory=Event)

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    @property
    def text(self) -> str:
        return self._text.text

    @property
    def text_shape(self) -> Vector2:
        return Vector2(*self._text.content_size)

    @property
    def font_size(self) -> float:
        return self._text.font_size

    @property
    def size_was_changed(self) -> OnEventSubscriber["TextUi", None]:
        return self._size_was_changed.subscriber

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._change_font_size_fitting(rectangle)
        self._set_text_position(rectangle)

    def set_text(self, text: str) -> None:
        self._text.text = text
        self.set_rectangle(self.rectangle)

    def set_color(self, color: Color) -> None:
        self._text.color = color

    def set_font_size(self, size: float, *, need_event: bool = True) -> None:
        self._text.font_size = size
        if need_event:
            self._size_was_changed.invoke(self)

    def _set_text_position(self, rectangle: Rectangle) -> None:
        if not self._is_center:
            self._text.position = rectangle.position
            return

        y = rectangle.center.y + self._text.font_size * HEIGHT_TO_WIDTH_RATIO / 10
        self._text.position = rectangle.center.with_y(y).tuple

    def _draw(self, _: Vector2) -> None:
        self._text.draw()

    def _change_font_size_fitting(self, rectangle: Rectangle) -> None:
        if rectangle == Rectangle.zero():
            return

        new_size = self._text.font_size
        for _ in range(3):
            rect_width, rect_height = rectangle.shape

            scale_x = rect_width / self.text_shape.x
            scale_y = rect_height / self.text_shape.y
            scale = min(scale_x, scale_y * HEIGHT_TO_WIDTH_RATIO)
            new_size = min(312, max(1, int(self._text.font_size * scale)))
            self.set_font_size(new_size, need_event=False)

        self.set_font_size(new_size)
