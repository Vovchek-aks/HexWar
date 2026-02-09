from attrs import frozen, field
import arcade as arc

import appearance.protocols as proto
from mathematics.hex_geometry import get_world_position
from mathematics.vector import Vector2Int
from appearance.graphics.sprites import Sprite

SpriteList = arc.sprite_list.SpriteList

SPRITES_SCALE_RATIO = 1.6


@frozen
class OnBoardSpritesDrawer(proto.OnBoardSpritesDrawer):
    @classmethod
    def make(cls, camera_orientation: proto.ReadonlyCameraOrientation) -> proto.OnBoardSpritesDrawer:
        self = cls(camera_orientation)
        camera_orientation.has_changed.subscribe(self._rotate_sprites)
        return self

    _camera_orientation: proto.ReadonlyCameraOrientation
    _sprite_list: SpriteList = field(init=False, factory=SpriteList)
    _sprites: dict[int, arc.Sprite] = field(init=False, factory=dict)

    def add_sprite(self, sprite: Sprite, coord: Vector2Int, *, scale_ratio: float = 1) -> int:
        arc_sprite = self._get_arc_sprite(sprite, coord, scale_ratio=scale_ratio)
        index = id(arc_sprite)
        self._sprite_list.append(arc_sprite)
        self._sprites[index] = arc_sprite
        return index

    def draw(self) -> None:
        self._sprite_list.draw()

    def remove_sprite(self, index: int) -> None:
        sprite = self._sprites.pop(index)
        self._sprite_list.remove(sprite)

    def _rotate_sprites(self) -> None:
        for sprite in self._sprites.values():
            sprite.angle = self._camera_orientation.rotation.degrees

    def _get_arc_sprite(self, sprite: Sprite, coord: Vector2Int, *, scale_ratio: float) -> arc.Sprite:
        position = get_world_position(coord)
        arc_sprite = arc.Sprite()
        arc_sprite.texture = sprite.get()
        arc_sprite.center_x = sprite.pivot.x
        arc_sprite.center_y = sprite.pivot.y
        arc_sprite.scale = self._resizing_ratio_for(sprite) * scale_ratio
        arc_sprite.position = position.tuple
        arc_sprite.angle = self._camera_orientation.rotation.degrees
        return arc_sprite

    @staticmethod
    def _resizing_ratio_for(sprite: Sprite) -> float:
        bigger_side = max(sprite.shape.x, sprite.shape.y)
        return SPRITES_SCALE_RATIO / bigger_side
