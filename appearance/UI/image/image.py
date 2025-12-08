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
        sprite = cls._reshape(sprite, rectangle)
        self = cls(drawer, sprite, rectangle)
        self._layer = (LayerBuilder()
                       .set_clicks_catcher(ShapeLayer(self._rectangle))
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

    @property
    def sprite(self) -> Sprite:
        return self._sprite

    def set_sprite(self, sprite: Sprite) -> None:
        self._sprite = self._reshape(sprite, self.rectangle)

    def set_rectangle(self, rectangle: Rectangle) -> None:
        self._rectangle = rectangle
        self._sprite = self._sprite.reshape(rectangle.shape.as_vector2int)
        self._layer = (LayerBuilder.like(self.layer)
                       .set_clicks_catcher(ShapeLayer(self._rectangle))
                       .build())

    def _draw(self, _: Vector2) -> None:
        self._drawer.draw_image(self._sprite, self.rectangle.left_up_corner)

    @staticmethod
    def _reshape(sprite: Sprite, rectangle: Rectangle) -> Sprite:
        return (sprite
                .reshape(Vector2Int.from_vector2(rectangle.shape, strict=False))
                .with_pivot(Vector2Int.zero()))
