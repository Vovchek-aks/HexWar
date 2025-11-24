from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite
from appearance.input.clicks_catcher.layers.shape_layer import ShapeLayer
from appearance.layer import LayerBuilder
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2, Vector2Int


@define
class ImageUi(proto.UiElement):
    @classmethod
    def make(cls, drawer: proto.UiDrawer, rectangle: Rectangle, sprite: Sprite) -> "ImageUi":
        self = cls(drawer, sprite.with_pivot(Vector2Int.zero()), rectangle)
        self._layer = (LayerBuilder()
                       .set_clicks_catching(ShapeLayer(self._rectangle))
                       .set_draw_function(self._draw)
                       .build())
        return self

    _drawer: proto.UiDrawer
    _sprite: Sprite
    _rectangle: Rectangle
    _layer: proto.Layer = field(init=False)

    @property
    def layer(self) -> proto.Layer:
        return self._layer

    @property
    def rectangle(self) -> Rectangle:
        return self._rectangle

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_image(self._sprite, self.rectangle.left_up_corner)
