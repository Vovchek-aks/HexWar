from pathlib import Path

from attrs import frozen

from core.protocols import Figure
from files import read_meta, read_json

LANGUAGE_SECTION_DICT = dict[str, str]
LANGUAGE_DICT = dict[str, LANGUAGE_SECTION_DICT]

LANGUAGES_META_DICT = dict[str, str | list[str]]

_SELECTED = "selected"

_INFO = "info"
_MESSAGES = "messages"

_FIGURES = "figures"

_UI = "ui"
_END_TURN_BTN = "END_TURN_BTN"
_PLAYERS_TURN_TEXT = "PLAYERS_TURN_TEXT"

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
    def _ui(self) -> LANGUAGE_SECTION_DICT:
        return self._messages[_UI]

    def get_figure_name(self, figure: type[Figure]) -> str:
        return self._figures.get(figure.__name__, figure.__name__)

    def get_end_turn_message(self) -> str:
        return self._ui[_END_TURN_BTN]

    def get_players_turn_message(self, player: str) -> str:
        return self._ui[_PLAYERS_TURN_TEXT].format(player=player)

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures
