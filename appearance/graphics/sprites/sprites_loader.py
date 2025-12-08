from pathlib import Path

from attrs import frozen

from core.protocols import Figure
from mathematics.vector import Vector2Int
from .sprite import Sprite
from files import read_meta

SPRITE_DICT = dict[str, str | list[int]]
SPRITES_GROUP_DICT = dict[str, SPRITE_DICT]
SPRITES_META_DICT = dict[str, SPRITE_DICT | SPRITES_GROUP_DICT]

_NO_SPRITE = "no_sprite"
_FILE = "file"
_PIVOT = "pivot"

_FIGURES = "figures"

_UI = "ui"
_BUTTON_2_TO_3 = "button_2_to_3"
_BUTTON_2_TO_3_ACTIVE = "button_2_to_3_active"
_BACKGROUND_2_to_3 = "background_2_to_3"

SPRITES_FOLDER = Path("data/sprites")


@frozen
class SpritesLoader:
    @staticmethod
    def _load_sprite(sprite_info: SPRITE_DICT) -> Sprite:
        file: str = sprite_info[_FILE]
        pivot: list[int] = sprite_info[_PIVOT]
        assert len(pivot) == 2

        path = SPRITES_FOLDER / file
        return Sprite.load_raw_image(path, Vector2Int(*pivot))

    @classmethod
    def from_meta(cls) -> "SpritesLoader":
        meta: SPRITES_META_DICT = read_meta(SPRITES_FOLDER)
        return cls(meta)

    _meta: SPRITES_META_DICT

    @property
    def _figures(self) -> SPRITES_GROUP_DICT:
        return self._meta[_FIGURES]

    @property
    def _ui(self) -> SPRITES_GROUP_DICT:
        return self._meta[_UI]

    def load_no_sprite(self) -> Sprite:
        sprite_info = self._meta[_NO_SPRITE]
        return self._load_sprite(sprite_info)

    def load_figure_sprite(self, figure: type[Figure]) -> Sprite:
        sprite_info = self._figures[figure.__name__]
        return self._load_sprite(sprite_info)

    def load_button_2_to_3(self) -> Sprite:
        sprite_info = self._ui[_BUTTON_2_TO_3]
        return self._load_sprite(sprite_info)

    def load_button_2_to_3_active(self) -> Sprite:
        sprite_info = self._ui[_BUTTON_2_TO_3_ACTIVE]
        return self._load_sprite(sprite_info)

    def load_background_2_to_3(self) -> Sprite:
        sprite_info = self._ui[_BACKGROUND_2_to_3]
        return self._load_sprite(sprite_info)


    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures
