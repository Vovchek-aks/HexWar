from attrs import define

from appearance.layer import LayerBuilder
from mathematics.vector import Vector2
import appearance.protocols as proto


@define
class TextUi(proto.Layer):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, text_data: proto.TextData) -> "TextUi":
        self = cls(drawer, text_data, ...)
        layer = (LayerBuilder()
                 .not_catching()
                 .set_draw_function(self._draw)
                 .build())
        self._layer = layer
        return self

    _drawer: proto.UiDrawer
    _data: proto.TextData
    _layer: proto.Layer

    @property
    def drawable_layer(self) -> proto.DrawableLayer:
        return self._layer.drawable_layer

    @property
    def clicks_catching_layer(self) -> proto.ClicksCatchingLayer:
        return self._layer.clicks_catching_layer

    def draw(self, mouse_position: Vector2) -> None:
        self._layer.drawable_layer.draw(mouse_position)

    def can_catch(self, click: proto.Click) -> bool:
        return self._layer.clicks_catching_layer.can_catch(click)

    def catch(self, click: proto.Click) -> None:
        self._layer.clicks_catching_layer.catch(click)

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_text(self._data)
