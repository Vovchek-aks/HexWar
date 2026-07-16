from attrs import frozen, field
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.colors import WHITE
from color import Color
from mathematics.hex_geometry import get_world_position
from mathematics.vector import Vector2Int
from appearance.graphics.sprites import Sprite

SPRITES_SCALE_RATIO = 1.6


@frozen
class OnBoardSpritesDrawer(proto.OnBoardSpritesDrawer):
    @classmethod
    def make(cls, camera_orientation: proto.ReadonlyCameraOrientation,
             pool: proto.SpritesPool) -> proto.OnBoardSpritesDrawer:
        self = cls(camera_orientation, pool)
        camera_orientation.has_changed.subscribe(self._rotate_sprites)
        return self

    _camera_orientation: proto.ReadonlyCameraOrientation
    _pool: proto.SpritesPool
    _sprites: dict[int, arc.Sprite] = field(init=False, factory=dict)
    _dont_need_rotation: set[int] = field(init=False, factory=set)

    def add_sprite(self,
                   sprite: Sprite,
                   coord: Vector2Int,
                   *,
                   color: Color = WHITE,
                   scale_ratio: float = 1,
                   need_rotation: bool = True) -> int:
        arc_sprite = self._pool.get(sprite)
        arc_sprite = self._prepare(arc_sprite, sprite, coord, scale_ratio=scale_ratio)
        arc_sprite.color = color
        index = id(arc_sprite)
        self._sprites[index] = arc_sprite
        if not need_rotation:
            self._dont_need_rotation.add(index)
        return index

    def get_sprite(self, index: int) -> arc.Sprite:
        assert index in self._sprites

        return self._sprites[index]

    def draw(self) -> None:
        self._pool.sprite_list.draw()

    def remove_sprite(self, index: int) -> None:
        assert index in self._sprites

        sprite = self._sprites.pop(index)
        self._pool.release(sprite)
        self._dont_need_rotation.discard(index)

    def discard_sprite(self, index: int) -> bool:
        if index not in self._sprites:
            return False

        self.remove_sprite(index)
        return True

    def _rotate_sprites(self) -> None:
        for index, sprite in self._sprites.items():
            if index not in self._dont_need_rotation:
                sprite.angle = self._camera_orientation.rotation.degrees

    def _prepare(self, arc_sprite: arc.Sprite, sprite: Sprite, coord: Vector2Int, *, scale_ratio: float) -> arc.Sprite:
        arc_sprite.visible = True
        arc_sprite.scale = self._resizing_ratio_for(sprite) * scale_ratio
        arc_sprite.position = get_world_position(coord).tuple
        arc_sprite.angle = self._camera_orientation.rotation.degrees
        return arc_sprite

    @staticmethod
    def _resizing_ratio_for(sprite: Sprite) -> float:
        bigger_side = max(sprite.shape.x, sprite.shape.y)
        return SPRITES_SCALE_RATIO / bigger_side
