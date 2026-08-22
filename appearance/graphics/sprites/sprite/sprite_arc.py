from pathlib import Path

import arcade as arc
from PIL import Image
from attrs import frozen

from mathematics.vector import Vector2Int, Vector2
from color import Color


@frozen
class Sprite:
    @classmethod
    def load_raw_image(cls, path: Path | str, pivot: Vector2Int = Vector2Int.zero()) -> "Sprite":
        path = Path(path)
        assert path.exists()

        image = arc.load_texture(path)
        return cls(image, Vector2Int(*image.size), pivot)

    _image: arc.Texture
    _shape: Vector2Int
    _pivot: Vector2Int = Vector2Int.zero()

    @property
    def shape(self) -> Vector2Int:
        return self._shape

    @property
    def pivot(self) -> Vector2Int:
        return self._pivot

    def get(self) -> arc.Texture:
        return self._image

    def blit_at(self, position: Vector2) -> None:
        screen_position = position - self._pivot.as_vector2
        arc.draw_texture_rect(self._image, arc.rect.XYWH(*screen_position,
                                                         *self.shape.tuple,
                                                         anchor=Vector2.zero()))

    def with_pivot(self, pivot: Vector2Int) -> "Sprite":
        return Sprite(self._image, self._shape, pivot)

    def with_pivot_from_ratios(self, ratio_x: float, ratio_y: float) -> "Sprite":
        pivot_x = int(self.shape.x * ratio_x)
        pivot_y = int(self.shape.y * ratio_y)
        pivot = Vector2Int(pivot_x, pivot_y)

        return Sprite(self._image, self._shape, pivot)

    def reshape(self, shape: Vector2Int) -> "Sprite":
        assert 0 not in shape.tuple
        pivot_x = int(self._pivot.x * (shape.x / self.shape.x))
        pivot_y = int(self._pivot.y * (shape.y / self.shape.y))
        pivot = Vector2Int(pivot_x, pivot_y)

        return Sprite(self._image, shape, pivot)

    def resize(self, ratio: float) -> "Sprite":
        shape = self.shape.scale_rounded(ratio)
        return self.reshape(shape)

    def colored_in(self, color: Color) -> "Sprite":
        r, g, b, a = self._image.image.split()
        r = r.point(lambda i: i * round(color.r) // 255)
        g = g.point(lambda i: i * round(color.g) // 255)
        b = b.point(lambda i: i * round(color.b) // 255)
        texture = arc.Texture(Image.merge("RGBA", (r, g, b, a)))

        return Sprite(texture, self._shape, self._pivot)
