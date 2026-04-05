from pathlib import Path

from attrs import frozen

from core.protocols import Figure
from mathematics.vector import Vector2Int
from .sprite import Sprite
from files import read_meta

SPRITES_FOLDER = Path("data/sprites")

SPRITE_DICT = dict[str, str | list[int]]
SPRITES_GROUP_DICT = dict[str, SPRITE_DICT]
SPRITES_META_DICT = dict[str, SPRITE_DICT | SPRITES_GROUP_DICT]

_NO_SPRITE = "no_sprite"
_FILE = "file"
_PIVOT = "pivot"

_FIGURES = "figures"

_UI = "ui"
_BUTTON_3_TO_2 = "button_3_to_2"
_BUTTON_3_TO_2_ACTIVE = "button_3_to_2_active"
_BACKGROUND_3_TO_2 = "background_3_to_2"
_BACKGROUND_2_TO_3 = "background_2_to_3"
_LOADING_SCREEN = "loading_screen"
_MENU_BACKGROUND = "menu_background"

_EFFECTS = "effects"
_EXPLOSION = "explosion"
_ROCKET = "rocket"


@frozen
class SpritesLoader:
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

    @property
    def _effects(self) -> SPRITES_GROUP_DICT:
        return self._meta[_EFFECTS]

    def load_no_sprite(self) -> Sprite:
        sprite_info = self._meta[_NO_SPRITE]
        return self._load_sprite(sprite_info)

    def load_figure_sprite(self, figure: type[Figure]) -> Sprite:
        assert self.has_figure(figure)

        sprite_info = self._figures[figure.__name__]
        return self._load_sprite(sprite_info)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures

    def load_button_3_to_2(self) -> Sprite:
        sprite_info = self._ui[_BUTTON_3_TO_2]
        return self._load_sprite(sprite_info)

    def load_button_3_to_2_active(self) -> Sprite:
        sprite_info = self._ui[_BUTTON_3_TO_2_ACTIVE]
        return self._load_sprite(sprite_info)

    def load_background_3_to_2(self) -> Sprite:
        sprite_info = self._ui[_BACKGROUND_3_TO_2]
        return self._load_sprite(sprite_info)

    def load_background_2_to_3(self) -> Sprite:
        sprite_info = self._ui[_BACKGROUND_2_TO_3]
        return self._load_sprite(sprite_info)

    def load_loading_screen(self) -> Sprite:
        sprite_info = self._ui[_LOADING_SCREEN]
        return self._load_sprite(sprite_info)

    def load_menu_background_screen(self) -> Sprite:
        sprite_info = self._ui[_MENU_BACKGROUND]
        return self._load_sprite(sprite_info)

    def load_explosion(self) -> Sprite:
        sprite_info = self._effects[_EXPLOSION]
        return self._load_sprite(sprite_info)

    def load_rocket(self) -> Sprite:
        sprite_info = self._effects[_ROCKET]
        return self._load_sprite(sprite_info)

    @staticmethod
    def _load_sprite(sprite_info: SPRITE_DICT) -> Sprite:
        file: str = sprite_info[_FILE]
        pivot: list[int] = sprite_info[_PIVOT]
        assert len(pivot) == 2

        path = SPRITES_FOLDER / file
        return Sprite.load_raw_image(path, Vector2Int(*pivot))
