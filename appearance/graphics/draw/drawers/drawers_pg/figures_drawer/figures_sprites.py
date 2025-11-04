from attrs import frozen

from appearance.graphics.sprites import Sprite
from core.protocols import Figure
import appearance.protocols as proto


@frozen
class FiguresSprites(proto.FiguresSprites):
    _sprites: dict[type[Figure], Sprite]
    _no_sprite: Sprite

    def get(self, figure: type[Figure]) -> Sprite:
        return self._sprites.get(figure, self._no_sprite)


@frozen
class FiguresSpritesBuilder:
    _no_sprite: Sprite
    _sprites = dict[type[Figure], Sprite]()

    def register(self, figure: type[Figure], sprite: Sprite) -> None:
        assert figure not in self._sprites

        self._sprites[figure] = sprite

    def build(self) -> proto.FiguresSprites:
        return FiguresSprites(self._sprites, self._no_sprite)
