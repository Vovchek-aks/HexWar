import math
from pathlib import Path

from attrs import frozen

from appearance.UI.number_shortener import NumberShortener
from appearance.settings import Settings
from core.moves.attack import Attack
from core.moves.capture import Capture
from core.moves.conversion import Conversion
from core.moves.pulling import PullingInitiation, PullingTermination
from core.moves.oreshnik_launch import OreshnikLaunch
from core.moves.relocations import Relocation, Assault
from core.protocols import Figure, Resource, Movable, CanLaunchOreshnik
from files import read_meta, read_json
import core.figures.figure as fig
from mathematics.vector import Vector2Int
from core.resources import ResourcesGroup

LANGUAGES_FOLDER = Path("data/languages")

LANGUAGE_SECTION_DICT = dict[str, str | list[str]] | list[list[list[str]]]
LANGUAGE_DICT = dict[str, LANGUAGE_SECTION_DICT | dict[str, LANGUAGE_SECTION_DICT]]

LANGUAGES_META_DICT = dict[str, str]

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

_FIGURES = "figures"

_RESOURCES = "resources"

_HINTS = "hints"
_CREATION = "creation"
_FIGURES_MENU = "figures_menu"
_TUTORIALS = "tutorials"

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
_STRENGTH = "STRENGTH"
_HARDNESS = "HARDNESS"
_COMBAT_ABILITY_COST = "COMBAT_ABILITY_COST"
_COST = "COST"
_FLOW = "FLOW"
_PAGE = "PAGE"
_NEXT = "NEXT"
_PLAYERS_TOP = "PLAYERS_TOP"
_TERRITORIES = "TERRITORIES"
_ECONOMY = "ECONOMY"

_MUSIC_VOLUME = "MUSIC_VOLUME"
_VOICE_VOLUME = "VOICE_VOLUME"
_EFFECTS_VOLUME = "EFFECTS_VOLUME"
_SELECTED_LANGUAGE = "SELECTED_LANGUAGE"
_SCREEN = "SCREEN"
_FULLSCREEN = "FULLSCREEN"
_WINDOWED = "WINDOWED"
_WIDTH = "WIDTH"
_HEIGHT = "HEIGHT"
_AUDIO = "AUDIO"
_GRAPHICS = "GRAPHICS"
_OTHER = "OTHER"
_APPLY = "APPLY"

_SELECTED_PLAYERS = "SELECTED_PLAYERS"
_NO_PLAYERS_SELECTED = "NO_PLAYERS_SELECTED"

_PLAY = "PLAY"
_TUTORIAL = "TUTORIAL"
_EXIT = "EXIT"
_AUTHORS = "AUTHORS"
_CYBER_DILF_ROLES = "CYBER_DILF_ROLES"
_DIVAN_ROLES = "DIVAN_ROLES"
_SETTINGS = "SETTINGS"
_BACK = "BACK"

_PAUSE = "PAUSE"
_CONTINUE = "CONTINUE"
_TO_MAIN_MENU = "TO_MAIN_MENU"

_LOADING = "loading"
_MAP_LOADING = "MAP_LOADING"
_INTERMEDIATE_PREPARING = "INTERMEDIATE_PREPARING"
_UI_MAKING = "UI_MAKING"
_SPRITE_LOADING = "SPRITE_LOADING"


@frozen
class Language:
    @classmethod
    def languages(cls) -> list[str]:
        meta: LANGUAGES_META_DICT = read_meta(LANGUAGES_FOLDER)
        return list(meta)

    @classmethod
    def from_meta(cls) -> "Language":
        meta: LANGUAGES_META_DICT = read_meta(LANGUAGES_FOLDER)
        settings = Settings.open()
        file = LANGUAGES_FOLDER / meta[settings.selected_language]
        json = read_json(file)
        messages = {
            _UI: Section(json[_UI]),
            _RESOURCES: Section(json[_RESOURCES]),
            _FIGURES: Section(json[_FIGURES]),
            _LOADING: Section(json[_LOADING]),
            _HINTS: {
                _CREATION: HintSection(json[_HINTS][_CREATION]),
                _FIGURES_MENU: HintSection(json[_HINTS][_FIGURES_MENU]),
                _TUTORIALS: json[_HINTS][_TUTORIALS]
            }
        }
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

    def get_tutorial_message(self) -> str:
        return self._ui[_TUTORIAL]

    def get_exit_message(self) -> str:
        return self._ui[_EXIT]

    def get_authors_message(self) -> str:
        return self._ui[_AUTHORS]

    def get_cyber_dilf_roles(self) -> list[str]:
        return self._ui[_CYBER_DILF_ROLES]

    def get_divan_roles(self) -> list[str]:
        return self._ui[_DIVAN_ROLES]

    def get_settings_message(self) -> str:
        return self._ui[_SETTINGS]

    def get_back_message(self) -> str:
        return self._ui[_BACK]

    def get_pause_message(self) -> str:
        return self._ui[_PAUSE]

    def get_continue_message(self) -> str:
        return self._ui[_CONTINUE]

    def get_to_main_menu_message(self) -> str:
        return self._ui[_TO_MAIN_MENU]

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

    def get_cost(self, resources: ResourcesGroup) -> list[str]:
        assert resources

        message = [f"{self._ui[_COST]}:"]
        message.extend([f"    {self.get_message_from_resource(resource)}"
                        for resource in resources
                        if resource.amount != 0])

        return message

    def get_flow_message(self) -> str:
        return self._ui[_FLOW]

    def get_page_message(self, page_index: int) -> str:
        return f"{self._ui[_PAGE]} {page_index + 1}"

    def get_next_message(self) -> str:
        return self._ui[_NEXT]

    def get_player_top_message(self) -> str:
        return self._ui[_PLAYERS_TOP]

    def get_territories_message(self) -> str:
        return self._ui[_TERRITORIES]

    def get_economy_message(self) -> str:
        return self._ui[_ECONOMY]

    def get_music_volume_message(self) -> str:
        return self._ui[_MUSIC_VOLUME]

    def get_voice_volume_message(self) -> str:
        return self._ui[_VOICE_VOLUME]

    def get_effects_volume_message(self) -> str:
        return self._ui[_EFFECTS_VOLUME]

    def get_selected_language_message(self) -> str:
        return self._ui[_SELECTED_LANGUAGE]

    def get_audio_message(self) -> str:
        return self._ui[_AUDIO]

    def get_graphics_message(self) -> str:
        return self._ui[_GRAPHICS]

    def get_screen_message(self) -> str:
        return self._ui[_SCREEN]

    def get_fullscreen_message(self) -> str:
        return self._ui[_FULLSCREEN]

    def get_windowed_message(self) -> str:
        return self._ui[_WINDOWED]

    def get_width_message(self) -> str:
        return self._ui[_WIDTH]

    def get_height_message(self) -> str:
        return self._ui[_HEIGHT]

    def get_other_message(self) -> str:
        return self._ui[_OTHER]

    def get_apply_message(self) -> str:
        return self._ui[_APPLY]

    def get_combat_ability_cost_message(self, combat_ability_ratio_cost: float) -> str:
        combat_ability_cost = f"{100 * combat_ability_ratio_cost:.0f}"
        return self._ui[_COMBAT_ABILITY_COST].format(combat_ability_cost=combat_ability_cost)

    def get_creation_hint(self, figure: type[Figure]) -> list[str]:
        return self._hints[_CREATION][figure.__name__]

    def get_figure_menu_hint_for(self, tag: str) -> list[str]:
        message = self._hints[_FIGURES_MENU][tag]
        message.append("")
        combat_ability_index = len(message)

        if tag == INFANTRY_TO_MOTORIZATION:
            resources, move_cost = Conversion.conversions()[fig.Infantry, fig.Motorization]
            budget = fig.Infantry.MOVES_BUDGET
        elif tag == MOTORIZATION_TO_INFANTRY:
            resources, move_cost = Conversion.conversions()[fig.Motorization, fig.Infantry]
            budget = fig.Motorization.MOVES_BUDGET
        elif tag == LAUNCH_ORESHNIK:
            resources = _FIGURE_OF_TAG[tag].FLAGS.get(CanLaunchOreshnik).cost
            move_cost = _FIGURE_OF_TAG[tag].get_cost_of(_MOVE_OF_TAG[tag]())
            budget = _FIGURE_OF_TAG[tag].MOVES_BUDGET
        else:
            resources = ResourcesGroup()
            move_cost = _FIGURE_OF_TAG[tag].get_cost_of(_MOVE_OF_TAG[tag]())
            budget = _FIGURE_OF_TAG[tag].MOVES_BUDGET

        if resources:
            message.append("")
            message.extend(self.get_cost(resources))

        combat_ability_cost_ratio = move_cost / budget
        message.insert(combat_ability_index, self.get_combat_ability_cost_message(combat_ability_cost_ratio))

        return message

    def get_combat_ability_message(self, figure: fig.Figure, spent: int) -> str:
        budget = figure.MOVES_BUDGET
        rest = budget - spent

        combat_ability_ratio = rest / budget
        combat_ability = f"{combat_ability_ratio:.0%}"

        form = self._ui[_COMBAT_ABILITY]
        if Movable in figure.FLAGS:
            relocations = math.floor(rest / figure.get_cost_of(Relocation(Vector2Int.zero(), Vector2Int.zero())))
            assaults = math.floor(rest / figure.get_cost_of(Assault(Vector2Int.zero(), Vector2Int.zero())))
            if relocations + assaults > 0:
                form = f"{form} ({relocations}/{assaults})"
                return form.format(combat_ability=combat_ability,
                                   relocations=str(relocations),
                                   assaults=str(assaults))

        return form.format(combat_ability=combat_ability)

    def get_strength_message(self, base: int, additional: int) -> str:
        return (self._ui[_STRENGTH].format(base=base) +
                (f" + {additional}" if additional > 0 else ""))

    def get_hardness_message(self, base: int, additional: int) -> str:
        return (self._ui[_HARDNESS].format(base=base) +
                (f" + {additional}" if additional > 0 else ""))

    def get_tutorial_hints(self, tutorial_index: int) -> list[list[str]]:
        return self._hints[_TUTORIALS][tutorial_index]

    def get_players_turn_message(self, player: str) -> str:
        return self._ui[_PLAYERS_TURN_TEXT].format(player=player)

    def get_selected_players_message(self, selected_players: list[str]) -> str:
        if not selected_players:
            return self._ui[_NO_PLAYERS_SELECTED]

        return f"{self._ui[_SELECTED_PLAYERS]}: {', '.join(selected_players)}."

    def has_figure(self, figure: type[Figure]) -> bool:
        return figure.__name__ in self._figures


class Section(dict[str, str]):
    def __getitem__(self, key: str) -> str:
        if key not in self:
            print(f"NO MESSAGE FOR [{key}] key")
            return key

        return super().__getitem__(key)


class HintSection(dict[str, list[str]]):
    def __getitem__(self, key: str) -> list[str]:
        if key not in self:
            print(f"NO MESSAGE FOR [{key}] key")
            return [key]

        return super().__getitem__(key)
