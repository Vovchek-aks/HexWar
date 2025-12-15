from pathlib import Path

from attrs import frozen

from appearance.UI.number_shortener import NumberShortener
from core.protocols import Figure, Resource
from files import read_meta, read_json

LANGUAGE_SECTION_DICT = dict[str, str | list[str]]
LANGUAGE_DICT = dict[str, LANGUAGE_SECTION_DICT | dict[str, LANGUAGE_SECTION_DICT]]

LANGUAGES_META_DICT = dict[str, str | list[str]]

_SELECTED = "selected"

_INFO = "info"
_MESSAGES = "messages"

_FIGURES = "figures"

_RESOURCES = "resources"

_HINTS = "hints"
_CREATION = "creation"

_UI = "ui"
_END_TURN_BTN = "END_TURN_BTN"
_PLAYERS_TURN_TEXT = "PLAYERS_TURN_TEXT"
_TO_MOTORIZATION = "TO_MOTORIZATION"
_CAPTURE = "CAPTURE"
_TO_INFANTRY = "TO_INFANTRY"
_ATTACK = "ATTACK"
_COMBAT_ABILITY = "COMBAT_ABILITY"
_COST = "COST"

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
    def _hints(self) -> dict[str, LANGUAGE_SECTION_DICT]:
        return self._messages[_HINTS]

    def get_figure_name(self, figure: type[Figure]) -> str:
        return self._figures.get(figure.__name__, figure.__name__)

    def get_resource_name(self, resource: type[Resource]) -> str:
        return self._resources.get(resource.__name__, resource.__name__)

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

    def get_message_from_resource(self, resource: Resource) -> str:
        amount = NumberShortener.shorten(resource.amount)
        return f"{self.get_resource_name(type(resource))}: {amount}"

    def get_cost(self, resource: Resource) -> list[str]:
        cost = self.get_message_from_resource(resource)
        message = [line.format(cost=cost) for line in self._ui[_COST]]

        return message

    def get_creation_hint(self, figure: type[Figure]) -> list[str]:
        return self._hints[_CREATION][figure.__name__]

    def get_combat_ability_message(self, combat_ability_ratio: float) -> str:
        combat_ability = f"{100 * combat_ability_ratio:.0f}"
        return self._ui[_COMBAT_ABILITY].format(combat_ability=combat_ability)

    def get_players_turn_message(self, player: str) -> str:
        return self._ui[_PLAYERS_TURN_TEXT].format(player=player)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures
