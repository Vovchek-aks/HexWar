from pathlib import Path

from attrs import frozen
import pygame as pg

from mathematics.vector import Vector2Int, Vector2


@frozen
class Sprite:
    @classmethod
    def load_raw_image(cls, path: Path | str, pivot: Vector2Int = Vector2Int.zero()) -> "Sprite":
        assert path.exists()

        return cls(pg.image.load(path).convert_alpha(), pivot)

    _image: pg.image
    _pivot: Vector2Int = Vector2Int.zero()

    @property
    def shape(self) -> Vector2Int:
        return Vector2Int(self._image.get_width(), self._image.get_height())

    def get(self) -> pg.image:
        return self._image

    def blit_on(self, screen: pg.Surface, position: Vector2) -> None:
        screen.blit(self._image, position - self._pivot.as_vector2)

    def with_pivot(self, pivot: Vector2Int) -> "Sprite":
        return type(self)(self._image, pivot)

    def with_pivot_from_ratios(self, ratio_x: float, ratio_y: float) -> "Sprite":
        pivot_x = int(self.shape.x * ratio_x)
        pivot_y = int(self.shape.y * ratio_y)
        pivot = Vector2Int(pivot_x, pivot_y)

        return type(self)(self._image, pivot)

    def reshape(self, shape: Vector2Int) -> "Sprite":
        image = pg.transform.scale(self._image, shape.tuple)

        pivot_x = int(self._pivot.x * (shape.x / self.shape.x))
        pivot_y = int(self._pivot.y * (shape.y / self.shape.y))
        pivot = Vector2Int(pivot_x, pivot_y)

        return type(self)(image, pivot)

    def resize(self, ratio: float) -> "Sprite":
        shape = self.shape.scale_rounded(ratio)
        return self.reshape(shape)
