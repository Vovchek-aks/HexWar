from pathlib import Path
import os
from typing import Callable

from attrs import frozen

from appearance.audio.sound.random_sound_player import RandomSoundPlayer
from appearance.audio.sound.switcher_sound_player import SwitcherSoundPlayer
from appearance.settings import Settings
from core.protocols import Figure
import appearance.protocols as proto
from appearance.audio.sound.sound_player import Sound
from appearance.audio.animation_sounds import AnimationSounds
from files import read_meta

SOUNDS_FOLDER = Path("data/sounds")
MUSIC_FOLDER = Path("data/music")
GAME_MUSIC_FOLDER = MUSIC_FOLDER / "game"
MENU_MUSIC_FILE = MUSIC_FOLDER / "menu.mp3"
PLAYER_SELECTION_MUSIC_FILE = MUSIC_FOLDER / "player_selection.mp3"

NESTED = dict[str, str | list[...]]  # recursive
FIGURES = dict[str, NESTED]
EFFECTS = dict[str, str | list[str]]
META = dict[str, str | FIGURES | EFFECTS]

_FIGURES_MAKER_OF: dict[str, Callable[[list[proto.SoundPlayer]], proto.SoundPlayer]] = {
    "variants": lambda sound_players: RandomSoundPlayer(sound_players),
    "loop": lambda sound_players: SwitcherSoundPlayer(sound_players)
}

_EMPTY_SOUND = "empty_sound"

_FIGURES = "figures"
_TYPE = "type"
_ELEMENTS = "elements"

_EFFECTS = "effects"
_CREATION_LANDING = "creation_landing"
_PULLING_INITIATION = "pulling_initiation"
_CONVERSION = "conversion"
_CAPTURE = "capture"
_ORESHNIK_FLIGHT = "oreshnik_flight"
_EXPLOSIONS = "explosions"
_ATTACKS = "attacks"
_INFANTRY_RELOCATIONS = "inf_reloc"
_TANK_RELOCATIONS = "tank_reloc"
_MOTORIZATION_RELOCATIONS = "mt_reloc"

_MUSIC_VOLUME_MULTIPLIER = .5


@frozen
class SoundsLoader:
    @classmethod
    def from_meta(cls) -> "SoundsLoader":
        meta: META = read_meta(SOUNDS_FOLDER)
        settings = Settings.open()
        return cls(meta, settings)

    _meta: META
    _settings: Settings

    @property
    def _figures(self) -> FIGURES:
        return self._meta[_FIGURES]

    @property
    def _effects(self) -> EFFECTS:
        return self._meta[_EFFECTS]

    def load_empty(self) -> Sound:
        return self._load_sound(self._meta[_EMPTY_SOUND])

    def load_figure_sound_player(self, figure: type[Figure]) -> proto.SoundPlayer:
        assert self.has_figure(figure)

        volume = self._settings.voice_volume
        nested = self._figures[figure.__name__]
        return self._load_nested(nested, volume)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures

    def load_animation_sounds(self, volume_multiplier: float) -> AnimationSounds:
        volume = self._settings.effects_volume * volume_multiplier
        return AnimationSounds(
            self.load_empty(),
            self._load_sound(self._effects[_CREATION_LANDING], volume=volume),
            self._load_sound(self._effects[_PULLING_INITIATION], volume=volume),
            self._load_sound(self._effects[_CONVERSION], volume=volume),
            self._load_sound(self._effects[_CAPTURE], volume=volume),
            self._load_sound(self._effects[_ORESHNIK_FLIGHT], volume=volume),
            self._load_random_effects(_EXPLOSIONS, volume),
            self._load_random_effects(_ATTACKS, volume),
            self._load_random_effects(_INFANTRY_RELOCATIONS, volume),
            self._load_random_effects(_MOTORIZATION_RELOCATIONS, volume),
            self._load_random_effects(_TANK_RELOCATIONS, volume),
        )

    def load_game_music(self) -> list[Sound]:
        volume = self._settings.music_volume * _MUSIC_VOLUME_MULTIPLIER
        sounds = list[Sound]()
        for file in os.listdir(GAME_MUSIC_FOLDER):
            sounds.append(Sound.load(GAME_MUSIC_FOLDER / file, is_streaming=True, volume=volume))
        return sounds

    def load_menu_music(self) -> Sound:
        volume = self._settings.music_volume * _MUSIC_VOLUME_MULTIPLIER
        return Sound.load(MENU_MUSIC_FILE, volume=volume, is_looped=True, is_streaming=True)

    def load_player_selection_music(self) -> Sound:
        volume = self._settings.music_volume * _MUSIC_VOLUME_MULTIPLIER
        return Sound.load(PLAYER_SELECTION_MUSIC_FILE, volume=volume, is_looped=True, is_streaming=True)

    def _load_random_effects(self, key: str, volume: float) -> RandomSoundPlayer:
        return RandomSoundPlayer([self._load_sound(file, volume=volume) for file in self._effects[key]],
                                 is_multiple_sounds_to_play_at_ones_allowed=True,
                                 is_repetitions_allowed=True)

    def _load_nested(self, nested: NESTED, volume: float = 1) -> proto.SoundPlayer:
        maker = _FIGURES_MAKER_OF[nested[_TYPE]]
        elements = nested[_ELEMENTS]
        if isinstance(elements, str):
            return maker(self._load_sounds_from(elements, volume))

        return maker(list(map(self._load_nested, elements)))

    @staticmethod
    def _load_sounds_from(folder: Path | str, volume: float = 1) -> list[Sound]:
        folder = SOUNDS_FOLDER / folder
        assert folder.is_dir()

        sounds = list[Sound]()
        for file in os.listdir(folder):
            sounds.append(Sound.load(folder / file, volume=volume))
        return sounds

    @staticmethod
    def _load_sound(path: Path | str, *, volume: float = 1) -> Sound:
        return Sound.load(SOUNDS_FOLDER / path, volume=volume)
