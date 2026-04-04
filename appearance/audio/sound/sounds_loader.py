from pathlib import Path
import os
from typing import Callable

from attrs import frozen

from appearance.audio.sound.random_sound_player import RandomSoundPlayer
from appearance.audio.sound.switcher_sound_player import SwitcherSoundPlayer
from core.protocols import Figure
import appearance.protocols as proto
from appearance.audio.sound.sound_player import Sound
from files import read_meta

SOUNDS_FOLDER = Path("data/sounds")
MUSIC_FOLDER = Path("data/music")

NESTED = dict[str, str | list[...]]  # recursive
FIGURES = dict[str, NESTED]
META = dict[str, str | FIGURES]

_FIGURES_MAKER_OF: dict[str, Callable[[list[proto.SoundPlayer]], proto.SoundPlayer]] = {
    "variants": lambda sound_players: RandomSoundPlayer(sound_players),
    "loop": lambda sound_players: SwitcherSoundPlayer(sound_players)
}

_EMPTY_SOUND = "empty_sound"

_FIGURES = "figures"
_TYPE = "type"
_ELEMENTS = "elements"


@frozen
class SoundsLoader:
    @classmethod
    def from_meta(cls) -> "SoundsLoader":
        meta: META = read_meta(SOUNDS_FOLDER)
        return cls(meta)

    _meta: META

    @property
    def _figures(self) -> FIGURES:
        return self._meta[_FIGURES]

    def load_empty(self) -> Sound:
        return self._load_sound(self._meta[_EMPTY_SOUND])

    def load_figure_sound_player(self, figure: type[Figure]) -> proto.SoundPlayer:
        assert self.has_figure(figure)

        nested = self._figures[figure.__name__]
        return self._load_nested(nested)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures

    @staticmethod
    def load_music(volume: float) -> list[Sound]:
        sounds = list[Sound]()
        for file in os.listdir(MUSIC_FOLDER):
            sounds.append(Sound.load(MUSIC_FOLDER / file, is_streaming=True, volume=volume))
        return sounds

    def _load_nested(self, nested: NESTED) -> proto.SoundPlayer:
        maker = _FIGURES_MAKER_OF[nested[_TYPE]]
        elements = nested[_ELEMENTS]
        if isinstance(elements, str):
            return maker(self._load_sounds_from(elements))

        return maker(list(map(self._load_nested, elements)))

    @staticmethod
    def _load_sounds_from(folder: Path | str) -> list[Sound]:
        folder = SOUNDS_FOLDER / folder
        assert folder.is_dir()

        sounds = list[Sound]()
        for file in os.listdir(folder):
            sounds.append(Sound.load(folder / file))
        return sounds

    @staticmethod
    def _load_sound(path: Path | str) -> Sound:
        return Sound.load(SOUNDS_FOLDER / path)
