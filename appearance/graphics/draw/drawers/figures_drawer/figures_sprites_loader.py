from typing import Callable

from attrs import frozen

from appearance.graphics.sprites import SpritesLoader
from core.protocols import Figure
import appearance.protocols as proto
from .figures_sprites import FiguresSpritesBuilder

_CALLBACK = Callable[[type[Figure]], None]
_FIGURES = list[type[Figure]]


@frozen
class FiguresSpritesLoader:
    _sprites_loader: SpritesLoader

    def load(self, figures: _FIGURES, on_no_figure: _CALLBACK = lambda figure: None) -> proto.FiguresSprites:
        builder = FiguresSpritesBuilder(self._sprites_loader.load_no_sprite())

        for figure in figures:
            if not self._sprites_loader.has_figure(figure):
                on_no_figure(figure)
                continue

            sprite = self._sprites_loader.load_figure_sprite(figure)
            builder.register(figure, sprite)

        return builder.build()
