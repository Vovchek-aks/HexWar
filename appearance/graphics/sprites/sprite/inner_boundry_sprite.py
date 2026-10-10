import arcade as arc
from attrs import frozen

from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING
from . import Sprite


@frozen
class InnerBoundrySprite(Sprite):
    @classmethod
    def from_sprite(cls, sprite: Sprite, rectangle: Rectangle) -> "InnerBoundrySprite":
        return cls(sprite._image, sprite._shape, sprite._pivot, rectangle)

    _rectangle: Rectangle = Rectangle.zero()

    def copy(self,
             *,
             image: Status | arc.Texture = MISSING,
             shape: Status | Vector2Int = MISSING,
             pivot: Status | Vector2Int = MISSING,
             rectangle: Status | Rectangle = MISSING) -> "Sprite":
        return type(self)(image or self._image,
                          shape or self._shape,
                          pivot or self._pivot,
                          rectangle or self._rectangle)

    def blit_at(self, position: Vector2) -> None:
        super().blit_at(position - self._rectangle.position)

    def reshape(self, shape: Vector2Int) -> "Sprite":
        assert shape

        if not self._rectangle.shape:
            return self.from_sprite(super().reshape(shape), self._rectangle)

        original = self.shape
        ratio_x = original.x / self._rectangle.shape.x
        ratio_y = original.y / self._rectangle.shape.y

        new_sprite = super().reshape(Vector2Int(round(shape.x * ratio_x),
                                                round(shape.y * ratio_y)))

        ratio_x = new_sprite.shape.x / original.x
        ratio_y = new_sprite.shape.y / original.y

        result = self.from_sprite(new_sprite,
                                  Rectangle(Vector2(self._rectangle.position.x * ratio_x,
                                                    self._rectangle.position.y * ratio_y),
                                            Vector2(self._rectangle.shape.x * ratio_x,
                                                    self._rectangle.shape.y * ratio_y)))
        return result
