from pathlib import Path

from attrs import frozen

import core.figures.figure as fig
from core.protocols import Resource
from mathematics.rectangle import Rectangle
from mathematics.vector import Vector2Int, Vector2
from .sprite import Sprite, InnerBoundrySprite
from files import read_meta
from appearance.figure_action_tags import ARTILLERY_ATTACK, HOWITZER_ATTACK, GRAD_ATTACK, TANK_ATTACK, \
    ARTILLERY_INITIATE_PULLING, ARTILLERY_TERMINATE_PULLING, MOTORIZATION_TO_INFANTRY, CAPITAL_TO_TALL_CAPITAL, \
    CAPITAL_TO_WIDE_CAPITAL, TANK_AND_ARTILLERY_TO_HOWITZER, MOTORIZATION_AND_ARTILLERY_TO_GRAD, PURCHASE_SETTLEMENT, \
    PURCHASE_PRIVATE_LIGHT_FACTORY, PURCHASE_PRIVATE_HEAVY_FACTORY, MOBILISE_TOWN, INFANTRY_CAPTURE, \
    INFANTRY_TO_MOTORIZATION, LAUNCH_ORESHNIK, MOBILISE_SETTLEMENT, INFANTRY_SETTLE

SPRITES_FOLDER = Path("data/sprites")

SPRITE_DICT = dict[str, str | list[int]]
SPRITES_GROUP_DICT = dict[str, SPRITE_DICT]
SPRITES_META_DICT = dict[str, SPRITE_DICT | SPRITES_GROUP_DICT]

_NO_SPRITE = "no_sprite"
_FILE = "file"
_PIVOT = "pivot"
_RECTANGLE = "rectangle"

_FIGURES = "figures"

_RESOURCES = "resources"
_COMBAT_ABILITY = "COMBAT_ABILITY"
_STRENGTH = "STRENGTH"
_HARDNESS = "HARDNESS"

_UI = "ui"
_MAP_EDITOR = "map_editor"
_BUTTON_3_TO_2 = "button_3_to_2"
_BUTTON_3_TO_2_ACTIVE = "button_3_to_2_active"
_BACKGROUND_3_TO_2 = "background_3_to_2"
_BACKGROUND_2_TO_3 = "background_2_to_3"
_LOADING_SCREEN = "loading_screen"
_MENU_BACKGROUND = "menu_background"
_LOGO = "logo"
_CYBER_DILF = "_cyberDilf"
_DIVAN = "divan"
_GITHUB = "github"
_TELEGRAM = "telegram"
_TWITCH = "twitch"
_ITCH = "itch"

_MAKE_BUTTONS_FOR: dict[type[fig.Figure], str] = {
    fig.Artillery: "make_art",
    fig.Bunker: "make_bunker",
    fig.TierOneCapital: "make_capital",
    fig.HeavyFactory: "make_hf",
    fig.LightFactory: "make_lf",
    fig.Infantry: "make_inf",
    fig.MissileSilo: "make_silo",
    fig.Tank: "make_tank",
    fig.Town: "make_town",
}

_ACTION_BUTTON_FOR = {
    ARTILLERY_ATTACK: "btn_attack",
    HOWITZER_ATTACK: "btn_attack",
    GRAD_ATTACK: "btn_grad_attack",
    TANK_ATTACK: "btn_attack",
    ARTILLERY_INITIATE_PULLING: "btn_connect",
    ARTILLERY_TERMINATE_PULLING: "btn_disconnect",
    MOTORIZATION_TO_INFANTRY: "btn_moto_to_inf",
    CAPITAL_TO_TALL_CAPITAL: "btn_capital_to_tall_capital",
    CAPITAL_TO_WIDE_CAPITAL: "btn_capital_to_wide_capital",
    TANK_AND_ARTILLERY_TO_HOWITZER: "btn_combine_with_art",
    MOTORIZATION_AND_ARTILLERY_TO_GRAD: "btn_combine_with_art",
    PURCHASE_SETTLEMENT: "btn_purchase",
    PURCHASE_PRIVATE_LIGHT_FACTORY: "btn_purchase",
    PURCHASE_PRIVATE_HEAVY_FACTORY: "btn_purchase",
    MOBILISE_TOWN: "btn_mobilise",
    MOBILISE_SETTLEMENT: "btn_mobilise",
    INFANTRY_SETTLE: "btn_inf_settle",
    INFANTRY_CAPTURE: "btn_inf_capture",
    INFANTRY_TO_MOTORIZATION: "btn_inf_to_moto",
    LAUNCH_ORESHNIK: "btn_launch_oreshnik",
}

_EFFECTS = "effects"
_EXPLOSION = "explosion"
_ROCKET = "rocket"
_WAVES = "waves"

_BOARD = "board"
_BACKGROUND1 = "background1"
_BACKGROUND2 = "background2"
_BACKGROUND3 = "background3"
_WATER = "water"


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
    def _resources(self) -> SPRITES_GROUP_DICT:
        return self._meta[_RESOURCES]

    @property
    def _effects(self) -> SPRITES_GROUP_DICT:
        return self._meta[_EFFECTS]

    @property
    def _board(self) -> SPRITES_GROUP_DICT:
        return self._meta[_BOARD]

    def load_no_sprite(self) -> Sprite:
        sprite_info = self._meta[_NO_SPRITE]
        return self._load_sprite(sprite_info)

    def load_figure_sprite(self, figure: type[fig.Figure]) -> Sprite:
        assert self.has_figure(figure)

        sprite_info = self._figures[figure.__name__]
        return self._load_sprite(sprite_info)

    def has_figure(self, figure: type[fig.Figure]) -> bool:
        return figure.__name__ in self._figures

    def load_resource_sprite(self, resource: type[Resource]) -> Sprite:
        sprite_info = self._resources[resource.__name__]
        return self._load_sprite(sprite_info)

    def load_combat_ability_icon(self) -> Sprite:
        sprite_info = self._resources[_COMBAT_ABILITY]
        return self._load_sprite(sprite_info)

    def load_strength_icon(self) -> Sprite:
        sprite_info = self._resources[_STRENGTH]
        return self._load_sprite(sprite_info)

    def load_hardness_icon(self) -> Sprite:
        sprite_info = self._resources[_HARDNESS]
        return self._load_sprite(sprite_info)

    def load_map_editor_icon(self) -> Sprite:
        sprite_info = self._ui[_MAP_EDITOR]
        return self._load_sprite(sprite_info)

    def load_button_3_to_2(self) -> Sprite:
        sprite_info = self._ui[_BUTTON_3_TO_2]
        return self._load_sprite(sprite_info)

    def load_figure_creation_button_for(self, figure: type[fig.Figure]) -> Sprite:
        sprite_info = self._ui[_MAKE_BUTTONS_FOR[figure]]
        return self._load_sprite(sprite_info)

    def load_action_button_for(self, action_tag: str) -> Sprite:
        sprite_info = self._ui[_ACTION_BUTTON_FOR[action_tag]]
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

    def load_menu_background(self) -> Sprite:
        sprite_info = self._ui[_MENU_BACKGROUND]
        return self._load_sprite(sprite_info)

    def load_logo(self) -> Sprite:
        sprite_info = self._ui[_LOGO]
        return self._load_sprite(sprite_info)

    def load_cyber_dilf(self) -> Sprite:
        sprite_info = self._ui[_CYBER_DILF]
        return self._load_sprite(sprite_info)

    def load_divan(self) -> Sprite:
        sprite_info = self._ui[_DIVAN]
        return self._load_sprite(sprite_info)

    def load_github(self) -> Sprite:
        sprite_info = self._ui[_GITHUB]
        return self._load_sprite(sprite_info)

    def load_telegram(self) -> Sprite:
        sprite_info = self._ui[_TELEGRAM]
        return self._load_sprite(sprite_info)

    def load_twitch(self) -> Sprite:
        sprite_info = self._ui[_TWITCH]
        return self._load_sprite(sprite_info)

    def load_itch(self) -> Sprite:
        sprite_info = self._ui[_ITCH]
        return self._load_sprite(sprite_info)

    def load_explosion(self) -> Sprite:
        sprite_info = self._effects[_EXPLOSION]
        return self._load_sprite(sprite_info)

    def load_rocket(self) -> Sprite:
        sprite_info = self._effects[_ROCKET]
        return self._load_sprite(sprite_info)

    def load_waves(self) -> Sprite:
        sprite_info = self._effects[_WAVES]
        return self._load_sprite(sprite_info)

    def load_background1(self) -> Sprite:
        sprite_info = self._board[_BACKGROUND1]
        return self._load_sprite(sprite_info)

    def load_background2(self) -> Sprite:
        sprite_info = self._board[_BACKGROUND2]
        return self._load_sprite(sprite_info)

    def load_background3(self) -> Sprite:
        sprite_info = self._board[_BACKGROUND3]
        return self._load_sprite(sprite_info)

    def load_water(self) -> Sprite:
        sprite_info = self._board[_WATER]
        return self._load_sprite(sprite_info)

    @staticmethod
    def _load_sprite(sprite_info: SPRITE_DICT) -> Sprite:
        file: str = sprite_info[_FILE]
        pivot: list[int] = sprite_info[_PIVOT]
        assert len(pivot) == 2

        path = SPRITES_FOLDER / file
        sprite = Sprite.load_raw_image(path, Vector2Int(*pivot))
        if _RECTANGLE not in sprite_info:
            return sprite

        rectangle = sprite_info[_RECTANGLE]
        assert len(rectangle) == 4

        position = Vector2(*rectangle[:2])
        shape = sprite.shape.as_vector2 - position - Vector2(*rectangle[-2:])
        return InnerBoundrySprite.from_sprite(sprite, Rectangle(position, shape))
