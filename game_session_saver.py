from collections import defaultdict
from pathlib import Path

from attrs import frozen

import core.protocols as proto
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.event_player_inputer import EventPlayerInputer
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from files import write_json
from mathematics.vector import Vector2Int
import core.figures.figure as fig

SAVE_FOLDER = Path("data") / "saves"

PLAYER_DICT = dict[str, str | list[str]]
BUDGET_DICT = dict[str, int]
PULLING_CONNECTIONS_DICT = dict[str, str]
FIGURES_DICT = dict[str, list[str]]
CELLS_LIST = list[int]
SESSION_DICT = dict[str, list[PLAYER_DICT] | BUDGET_DICT | PULLING_CONNECTIONS_DICT | FIGURES_DICT | CELLS_LIST]

_PLAYERS = "PLAYERS"
_NAME = "NAME"
_COLOR = "COLOR"
_INPUTER = "INPUTER"

_BUDGET = "BUDGET"

_PULLABLE_OF = "PULLABLE_OF"

_FIGURES = "FIGURES"

_CELLS = "CELLS"


@frozen
class GameSessionSaver:
    _session: proto.GameSession

    def save(self, filename: str) -> None:
        json = self._get_json()
        write_json(json, SAVE_FOLDER / filename)

    def _get_json(self) -> SESSION_DICT:
        json = SESSION_DICT()
        json[_PLAYERS] = self._get_player_dicts()
        json[_BUDGET] = self._get_budget_dict()
        json[_PULLABLE_OF] = self._get_pulling_connections_dict()
        json[_FIGURES] = self.get_figures_dict()
        json[_CELLS] = self._get_cells_list()
        return json

    def _get_player_dicts(self) -> list[PLAYER_DICT]:
        players = list[PLAYER_DICT]()
        for player in self._session.master.players:
            players.append({
                _NAME: player.data.name,
                _COLOR: player.data.color.hex(),
                _INPUTER: self._get_player_inputer_list(player.inputer),
            })
        return players

    def _get_budget_dict(self) -> BUDGET_DICT:
        budget = BUDGET_DICT()
        for figure, bill in self._session.figures_budget.figures_bills.items():
            coord = self._session.figures.locate(figure)
            budget[self._key_from(coord)] = bill
        return budget

    def _get_pulling_connections_dict(self) -> PULLING_CONNECTIONS_DICT:
        connections = PULLING_CONNECTIONS_DICT()
        for puller, pullable in self._session.pulling_connections.pullable_of.items():
            puller_coord = self._session.figures.locate(puller)
            pullable_coord = self._session.figures.locate(pullable)
            connections[self._key_from(puller_coord)] = self._key_from(pullable_coord)
        return connections

    def get_figures_dict(self) -> FIGURES_DICT:
        figures: FIGURES_DICT = defaultdict(list)
        for figure in fig.get_figures():
            if proto.Empty in figure.FLAGS:
                continue

            cells = self._session.cells.with_figure(figure)
            if not cells:
                continue

            for cell in cells:
                coord = self._session.board.coordinates_of(cell)
                figures[figure.__name__].append(self._key_from(coord))

        return figures

    def _get_cells_list(self) -> CELLS_LIST:
        cells = CELLS_LIST()
        for coord in self._session.board.cell_coords:
            cell = self._session.board[coord]
            if not cell.figure.is_on_land():
                cells.append(-1)
                continue

            player_index = self._session.master.players.index(cell.owner)
            cells.append(player_index)
        return cells

    @staticmethod
    def _get_player_inputer_list(inputer: proto.PlayerInputer) -> list[str]:
        name = inputer.__class__.__name__
        match inputer:
            case BotPlayerInputer():
                return [name, inputer.bot.__class__.__name__]
            case EventPlayerInputer():
                return [WantsToBeEventPlayerInputer.__name__]
        return [name]

    @staticmethod
    def _key_from(coord: Vector2Int) -> str:
        return f"{coord.x} {coord.y}"
