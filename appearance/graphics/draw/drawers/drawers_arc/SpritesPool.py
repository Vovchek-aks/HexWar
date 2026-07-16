import math
from collections import defaultdict

from attrs import frozen, field
import arcade as arc

import appearance.protocols as proto
from appearance.graphics.sprites import Sprite

SpriteList = arc.sprite_list.SpriteList

DEFAULT_COUNT = 0


@frozen
class SpritesPool(proto.SpritesPool):
    @classmethod
    def make(cls,
             *,
             count_multiplier_of_sprites: dict[Sprite, float],
             pool_count=DEFAULT_COUNT) -> "SpritesPool":
        self = cls()

        for sprite, multiplier in count_multiplier_of_sprites.items():
            texture = sprite.get()
            assert texture not in self._pool

            for _ in range(math.ceil(pool_count * multiplier)):
                arc_sprite = arc.Sprite(texture)
                arc_sprite.visible = False
                self._pool[texture].append(arc_sprite)
                self._sprite_list.append(arc_sprite)

        return self

    _pool: dict[arc.Texture, list[arc.Sprite]] = field(init=False, factory=lambda: defaultdict(list))
    _sprite_list: SpriteList = field(init=False, factory=lambda: SpriteList(capacity=10_000))

    @property
    def sprite_list(self) -> SpriteList:
        return self._sprite_list

    def get(self, sprite: Sprite) -> arc.Sprite:
        texture = sprite.get()
        if self._pool[texture]:
            return self._pool[texture].pop()

        arc_sprite = arc.Sprite(texture)
        self._sprite_list.append(arc_sprite)
        return arc_sprite

    def release(self, arc_sprite: arc.Sprite) -> None:
        arc_sprite.visible = False
        self._pool[arc_sprite.texture].append(arc_sprite)
