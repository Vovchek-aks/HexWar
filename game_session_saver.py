import os
from collections import defaultdict
from pathlib import Path

from attrs import frozen

import core.protocols as proto
from color import Color
from core.board import Board
from core.cell import Cell
from core.cells_cache import CellsCache
from core.figures.figures import Figures
from core.figures.figures_relocation_budget import FiguresRelocationBudget
from core.game_session import GameSession
from core.master import Master
from core.player import Player, PlayerData
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.event_player_inputer import EventPlayerInputer
from core.player.inputers.pass_player_inputer import PassPlayerInputer
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from core.pulling_connections import PullingConnections
from files import write_json, read_json
from mathematics.vector import Vector2Int
import core.figures.figure as fig
from core.player.inputers.bots import bots
from core.resources import get_resources_types, ResourcesStockpile, ResourcesGroup
from statuses import MISSING

SAVE_FOLDER = Path("data") / "saves"

SAVE_FILE = Path("last_save.json")
EDIT_MAP_FILE = Path("_edit_map.json")

PLAYER_DICT = dict[str, str | list[str] | dict[str, int]]
BUDGET_DICT = dict[str, int]
PULLING_CONNECTIONS_DICT = dict[str, str]
FIGURES_DICT = dict[str, list[str]]
CELLS_LIST = list[int]
SESSION_DICT = dict[str, list[PLAYER_DICT] | BUDGET_DICT | PULLING_CONNECTIONS_DICT | FIGURES_DICT | str | CELLS_LIST]

BOTS = {bot.__name__: bot for bot in bots}
RESOURCES = {resource.__name__: resource for resource in get_resources_types()}
FIGURES = {figure.__name__: figure for figure in fig.get_figures()}

_PLAYERS = "PLAYERS"
_NAME = "NAME"
_COLOR = "COLOR"
_INPUTER = "INPUTER"
_RESOURCES = "RESOURCES"

_BUDGET = "BUDGET"

_PULLABLE_OF = "PULLABLE_OF"

_FIGURES = "FIGURES"

_BOARD_SHAPE = "BOARD_SHAPE"

_CELLS = "CELLS"

_TUTORIAL_MAP_PREFIX = "Tutorial"


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
        json[_BOARD_SHAPE] = self._key_from(self._session.board.shape)
        json[_CELLS] = self._get_cells_list()
        return json

    def _get_player_dicts(self) -> list[PLAYER_DICT]:
        players = list[PLAYER_DICT]()
        for player in self._session.master.players:
            players.append({
                _NAME: player.data.name,
                _COLOR: player.data.color.hex(),
                _INPUTER: self._get_player_inputer_list(player.inputer),
                _RESOURCES: self._get_player_resources_dict(player.resources)
            })
        return players

    @staticmethod
    def _get_player_inputer_list(inputer: proto.PlayerInputer) -> list[str]:
        name = inputer.__class__.__name__
        match inputer:
            case BotPlayerInputer():
                return [name, inputer.bot.__class__.__name__]
            case PassPlayerInputer():
                return [name, inputer.timeout]
            case EventPlayerInputer():
                return [WantsToBeEventPlayerInputer.__name__]
        return [name]

    @staticmethod
    def _get_player_resources_dict(resources: proto.ResourcesStockpile) -> dict[str, int]:
        resources_dict = dict[str, int]()
        for name, resource in RESOURCES.items():
            resources_dict[name] = resources.get(resource).amount
        return resources_dict

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
        board = self._session.board
        for coord in board.cell_coords:
            cell = board[coord]
            if not cell.figure.is_on_land():
                cells.append(-1)
                continue

            player_index = self._session.master.players.index(cell.owner)
            cells.append(player_index)
        return cells

    @staticmethod
    def _key_from(coord: Vector2Int) -> str:
        return f"{coord.x} {coord.y}"


@frozen
class GameSessionLoader:
    @classmethod
    def make(cls, filename: str, ups: int) -> "GameSessionLoader":
        return cls(read_json(SAVE_FOLDER / filename), ups)

    _json: SESSION_DICT
    _ups: int

    def load(self) -> GameSession:
        master = self._load_master()
        board = self._load_board(master)
        figures = self._load_figures(board)
        pulling_connections = self._load_pulling_connections(board, figures)
        budget = self._load_figures_budget(board)
        cells = CellsCache.make(board)

        return GameSession(master, board, budget, pulling_connections, cells, figures)

    def _load_master(self) -> Master:
        players = list[proto.Player]()
        for player_info in self._json[_PLAYERS]:
            name = player_info[_NAME]
            color = Color.from_hex_string(player_info[_COLOR])
            inputer = self._load_inputer(player_info[_INPUTER])
            resources = self._load_resources(player_info[_RESOURCES])
            players.append(Player(PlayerData(color, name), inputer, resources))
        return Master(players)

    def _load_inputer(self, inputer_info: list[str]) -> proto.PlayerInputer:
        match inputer_info[0]:
            case BotPlayerInputer.__name__:
                bot = BOTS[inputer_info[1]]()
                return BotPlayerInputer(bot, 1 / self._ups)
            case PassPlayerInputer.__name__:
                return PassPlayerInputer(float(inputer_info[1]))
            case WantsToBeEventPlayerInputer.__name__:
                return WantsToBeEventPlayerInputer()

        raise NotImplementedError(inputer_info[0])

    @staticmethod
    def _load_resources(resources: dict[str, int]) -> ResourcesStockpile:
        stockpile = ResourcesStockpile()
        for name, amount in resources.items():
            stockpile.add(ResourcesGroup.make(RESOURCES[name](amount)))
        return stockpile

    def _load_board(self, master: Master) -> Board:
        shape = self._coord_from(self._json[_BOARD_SHAPE])
        codes = self._json[_CELLS]
        magic_dict = dict(zip(Board.get_cell_coords(shape),
                              map(lambda code: self._parse_cell(code, master), codes)))
        return Board.from_maker(shape, magic_dict.get)

    @staticmethod
    def _parse_cell(code: int, master: Master) -> Cell:
        if code == -1:
            return Cell(MISSING, fig.Water())

        return Cell(master.players[code], fig.Land())

    def _load_figures(self, board: Board) -> Figures:
        figures = Figures(board)
        figures_info: FIGURES_DICT = self._json[_FIGURES]
        for figure_name, keys in figures_info.items():
            figure = FIGURES[figure_name]
            for coord in map(self._coord_from, keys):
                figures.add(figure, coord)

        return figures

    def _load_pulling_connections(self, board: Board, figures: Figures) -> PullingConnections:
        connections = PullingConnections.make(figures)
        pullable_of: PULLING_CONNECTIONS_DICT = self._json[_PULLABLE_OF]
        for puller_key, pullable_key in pullable_of.items():
            connections.register(board[self._coord_from(puller_key)].figure,
                                 board[self._coord_from(pullable_key)].figure)
        return connections

    def _load_figures_budget(self, board: Board) -> FiguresRelocationBudget:
        budget = FiguresRelocationBudget()
        bill_of: BUDGET_DICT = self._json[_BUDGET]
        for key, bill in bill_of.items():
            budget.add(board[self._coord_from(key)].figure, bill)
        return budget

    @staticmethod
    def _coord_from(key: str) -> Vector2Int:
        return Vector2Int(*map(int, key.split()))


def _get_all_maps() -> list[str]:
    maps = list[str]()
    for file in map(Path, os.listdir(SAVE_FOLDER)):
        if file.suffix != ".json":
            continue

        if file.stem.startswith('_'):
            continue

        maps.append(file.stem)

    if SAVE_FILE.stem in maps:
        maps.remove(SAVE_FILE.stem)
        maps.insert(0, SAVE_FILE.stem)

    return maps


def get_saved_maps() -> list[str]:
    return [map_name for map_name in _get_all_maps() if not is_tutorial(map_name)]


def get_tutorials() -> list[str]:
    return [map_name for map_name in _get_all_maps() if is_tutorial(map_name)]


def is_tutorial(map_name: str) -> bool:
    return map_name.startswith(_TUTORIAL_MAP_PREFIX)
