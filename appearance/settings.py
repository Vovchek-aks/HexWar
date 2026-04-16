from pathlib import Path

from attrs import frozen

from files import read_json, write_json
from mathematics.vector import Vector2Int

SETTINGS_FILE = Path("data/settings.json")

SECTION = dict[str, float | str | bool]
SETTINGS = dict[str, SECTION | dict[str, SECTION]]

LANGUAGE = "language"
SELECTED = "SELECTED"

AUDIO = "audio"
MUSIC = "music"
VOICE = "voice"
EFFECTS = "effects"
VOLUME = "VOLUME"

GRAPHICS = "graphics"
SCREEN = "screen"
WIDTH = "WIDTH"
HEIGHT = "HEIGHT"
IS_FULLSCREEN = "IS_FULLSCREEN"


@frozen
class Settings:
    @classmethod
    def open(cls) -> "Settings":
        settings = read_json(SETTINGS_FILE)
        return cls(settings)

    @classmethod
    def from_keys(cls, keys: dict[str, str | float]) -> "Settings":
        settings = {
            LANGUAGE: {
                SELECTED: keys[LANGUAGE]
            },
            AUDIO: {
                MUSIC: {
                    VOLUME: keys[MUSIC]
                },
                VOICE: {
                    VOLUME: keys[VOICE]
                },
                EFFECTS: {
                    VOLUME: keys[EFFECTS]
                }
            },
            GRAPHICS: {
                SCREEN: {
                    WIDTH: keys[WIDTH],
                    HEIGHT: keys[HEIGHT],
                    IS_FULLSCREEN: keys[IS_FULLSCREEN]
                }
            }
        }
        return cls(settings)

    _settings: SETTINGS

    @property
    def selected_language(self) -> str:
        return self._settings[LANGUAGE][SELECTED]

    @property
    def music_volume(self) -> float:
        return self._audio[MUSIC][VOLUME]

    @property
    def voice_volume(self) -> float:
        return self._audio[VOICE][VOLUME]

    @property
    def effects_volume(self) -> float:
        return self._audio[EFFECTS][VOLUME]

    @property
    def if_fullscreen(self) -> bool:
        return self._graphics[SCREEN][IS_FULLSCREEN]

    @property
    def screen_shape(self) -> Vector2Int:
        width = self._graphics[SCREEN][WIDTH]
        height = self._graphics[SCREEN][HEIGHT]
        return Vector2Int(width, height)

    @property
    def _audio(self) -> dict[str, SECTION]:
        return self._settings[AUDIO]

    @property
    def _graphics(self) -> dict[str, SECTION]:
        return self._settings[GRAPHICS]

    def save(self) -> None:
        write_json(self._settings, SETTINGS_FILE)
