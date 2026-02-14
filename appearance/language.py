from pathlib import Path

from attrs import frozen

from appearance.UI.number_shortener import NumberShortener
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.conversion import Conversion
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.oreshnik_launch import OreshnikLaunch
from core.protocols import Figure, Resource
from files import read_meta, read_json
import core.figures.figure as fig
from mathematics.vector import Vector2Int

LANGUAGE_SECTION_DICT = dict[str, str | list[str]]
LANGUAGE_DICT = dict[str, LANGUAGE_SECTION_DICT | dict[str, LANGUAGE_SECTION_DICT]]

LANGUAGES_META_DICT = dict[str, str | list[str]]

ARTILLERY_ATTACK = "ARTILLERY_ATTACK"
TANK_ATTACK = "TANK_ATTACK"
ARTILLERY_INITIATE_PULLING = "ARTILLERY_INITIATE_PULLING"
ARTILLERY_TERMINATE_PULLING = "ARTILLERY_TERMINATE_PULLING"
MOTORIZATION_TO_INFANTRY = "MOTORIZATION_TO_INFANTRY"
INFANTRY_CAPTURE = "INFANTRY_CAPTURE"
INFANTRY_TO_MOTORIZATION = "INFANTRY_TO_MOTORIZATION"
LAUNCH_ORESHNIK = "LAUNCH_ORESHNIK"

_FIGURE_OF_TAG: dict[str, type[Figure]] = {
    INFANTRY_CAPTURE: fig.Infantry,
    TANK_ATTACK: fig.Tank,
    ARTILLERY_ATTACK: fig.Artillery,
    ARTILLERY_INITIATE_PULLING: fig.Artillery,
    ARTILLERY_TERMINATE_PULLING: fig.Artillery,
    LAUNCH_ORESHNIK: fig.MissileSilo,
}

_MOVE_OF_TAG = {
    INFANTRY_CAPTURE: lambda: Capture(Vector2Int.zero(), Vector2Int.zero()),
    TANK_ATTACK: lambda: Attack(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_ATTACK: lambda: Attack(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_INITIATE_PULLING: lambda: PullingInitiation(Vector2Int.zero(), Vector2Int.zero()),
    ARTILLERY_TERMINATE_PULLING: lambda: PullingTermination(Vector2Int.zero()),
    LAUNCH_ORESHNIK: lambda: OreshnikLaunch(Vector2Int.zero(), Vector2Int.zero())
}

_SELECTED = "selected"

_INFO = "info"
_MESSAGES = "messages"

_FIGURES = "figures"

_RESOURCES = "resources"

_HINTS = "hints"
_CREATION = "creation"
_FIGURES_MENU = "figures_menu"

_UI = "ui"
_END_TURN_BTN = "END_TURN_BTN"
_PLAYERS_TURN_TEXT = "PLAYERS_TURN_TEXT"
_TO_MOTORIZATION = "TO_MOTORIZATION"
_CAPTURE = "CAPTURE"
_TO_INFANTRY = "TO_INFANTRY"
_ATTACK = "ATTACK"
_INITIATE_PULLING = "INITIATE_PULLING"
_TERMINATE_PULLING = "TERMINATE_PULLING"
_LAUNCH_ORESHNIK = "LAUNCH_ORESHNIK"
_COMBAT_ABILITY = "COMBAT_ABILITY"
_COMBAT_ABILITY_COST = "COMBAT_ABILITY_COST"
_COST = "COST"
_PLAY = "PLAY"
_EXIT = "EXIT"

_LOADING = "loading"
_MAP_LOADING = "MAP_LOADING"
_INTERMEDIATE_PREPARING = "INTERMEDIATE_PREPARING"
_UI_MAKING = "UI_MAKING"
_SPRITE_LOADING = "SPRITE_LOADING"

LANGUAGES_FOLDER = Path("data/languages")


@frozen
class Language:
    @staticmethod
    def _get_message(section: LANGUAGE_SECTION_DICT, key: str) -> str:
        if key not in section:
            print(f"NO MESSAGE FOR {key}")

        return section.get(key, key)

    @classmethod
    def from_meta(cls) -> "Language":
        meta: LANGUAGES_META_DICT = read_meta(LANGUAGES_FOLDER)
        selected = LANGUAGES_FOLDER / meta[_SELECTED]
        messages = read_json(selected)[_MESSAGES]
        return cls(messages)

    _messages: LANGUAGE_DICT

    @property
    def _figures(self) -> LANGUAGE_SECTION_DICT:
        return self._messages[_FIGURES]

    @property
    def _resources(self) -> LANGUAGE_SECTION_DICT:
        return self._messages[_RESOURCES]

    @property
    def _ui(self) -> LANGUAGE_SECTION_DICT:
        return self._messages[_UI]

    @property
    def _loading(self) -> LANGUAGE_SECTION_DICT:
        return self._messages[_LOADING]

    @property
    def _hints(self) -> dict[str, LANGUAGE_SECTION_DICT]:
        return self._messages[_HINTS]

    def get_figure_name(self, figure: type[Figure]) -> str:
        return self._figures.get(figure.__name__, figure.__name__)

    def get_resource_name(self, resource: type[Resource]) -> str:
        return self._resources.get(resource.__name__, resource.__name__)

    def get_map_loading_message(self) -> str:
        return self._loading[_MAP_LOADING]

    def get_intermediate_preparing_message(self) -> str:
        return self._loading[_INTERMEDIATE_PREPARING]

    def get_ui_making_message(self) -> str:
        return self._loading[_UI_MAKING]

    def get_sprite_loading_message(self) -> str:
        return self._loading[_SPRITE_LOADING]

    def get_play_message(self) -> str:
        return self._ui[_PLAY]

    def get_exit_message(self) -> str:
        return self._ui[_EXIT]

    def get_end_turn_message(self) -> str:
        return self._ui[_END_TURN_BTN]

    def get_to_motorize_message(self) -> str:
        return self._ui[_TO_MOTORIZATION]

    def get_to_infantry_message(self) -> str:
        return self._ui[_TO_INFANTRY]

    def get_capture_message(self) -> str:
        return self._ui[_CAPTURE]

    def get_attack_message(self) -> str:
        return self._ui[_ATTACK]

    def get_initiate_pulling_message(self) -> str:
        return self._ui[_INITIATE_PULLING]

    def get_terminate_pulling_message(self) -> str:
        return self._ui[_TERMINATE_PULLING]

    def get_launch_oreshnik_message(self) -> str:
        return self._ui[_LAUNCH_ORESHNIK]

    def get_message_from_resource(self, resource: Resource) -> str:
        amount = NumberShortener.shorten(resource.amount)
        return f"{self.get_resource_name(type(resource))}: {amount}"

    def get_cost(self, resource: Resource) -> list[str]:
        cost = self.get_message_from_resource(resource)
        message = [line.format(cost=cost) for line in self._ui[_COST]]

        return message

    def get_combat_ability_cost_message(self, combat_ability_ratio_cost: float) -> str:
        combat_ability_cost = f"{100 * combat_ability_ratio_cost:.0f}"
        return self._ui[_COMBAT_ABILITY_COST].format(combat_ability_cost=combat_ability_cost)

    def get_creation_hint(self, figure: type[Figure]) -> list[str]:
        return self._hints[_CREATION][figure.__name__]

    def get_figure_menu_hint_for(self, tag: str) -> list[str]:
        message = self._hints[_FIGURES_MENU][tag]
        if tag == INFANTRY_TO_MOTORIZATION:
            cost, move_cost = Conversion.conversions()[fig.Infantry, fig.Motorization]
            budget = fig.Infantry.MOVES_BUDGET
            message = [line.format(cost=self.get_message_from_resource(cost)) for line in message]
        elif tag == MOTORIZATION_TO_INFANTRY:
            _, move_cost = Conversion.conversions()[fig.Motorization, fig.Infantry]
            budget = fig.Motorization.MOVES_BUDGET
        else:
            move_cost = _FIGURE_OF_TAG[tag].get_cost_of(_MOVE_OF_TAG[tag]())
            budget = _FIGURE_OF_TAG[tag].MOVES_BUDGET

        combat_ability_cost_ratio = move_cost / budget
        message.append(self.get_combat_ability_cost_message(combat_ability_cost_ratio))

        return message

    def get_combat_ability_message(self, combat_ability_ratio: float) -> str:
        combat_ability = f"{100 * combat_ability_ratio:.0f}"
        return self._ui[_COMBAT_ABILITY].format(combat_ability=combat_ability)

    def get_players_turn_message(self, player: str) -> str:
        return self._ui[_PLAYERS_TURN_TEXT].format(player=player)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures
