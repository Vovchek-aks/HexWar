from typing import Callable

from attrs import frozen

import appearance.protocols as proto
import core.figures.figure as fig
from appearance.audio.sound.sounds_loader import SoundsLoader


@frozen
class FiguresSounds:
    @classmethod
    def load(cls, on_no_figure: Callable[[type[fig.Figure]], None] = lambda figure: None) -> "FiguresSounds":
        sounds_loader = SoundsLoader.from_meta()
        sound_player_of = dict[type[fig.Figure], proto.SoundPlayer]()
        for figure in fig.get_figures():
            if not sounds_loader.has_figure(figure):
                on_no_figure(figure)
                continue
            sound_player_of[figure] = sounds_loader.load_figure_sound_player(figure)

        return cls(sound_player_of, sounds_loader.load_empty())

    _sound_player_of: dict[type[fig.Figure], proto.SoundPlayer]
    _empty_sound: proto.SoundPlayer

    def get_for(self, figure: type[fig.Figure]) -> proto.SoundPlayer:
        return self._sound_player_of.get(figure, self._empty_sound).copy()
