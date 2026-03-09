import random

from attrs import frozen

import core.protocols as proto
from core.cells_cache import CellsCache
from core.figures.figures import Figures
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots.bot_igor import BotIgor
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from core.pulling_connections import PullingConnections
from core.resources import Dollars
from mathematics.vector import Vector2Int
from appearance.graphics import colors
from core.board import Board
from core.cell import Cell
from core.figures.figures_relocation_budget import FiguresRelocationBudget
from core.master import Master
from core.player import PlayerData, Player
import core.figures.figure as fig
from statuses import MISSING


@frozen
class GameSession(proto.GameSession):
    _master: proto.Master
    _board: proto.Board
    _figures_budget: proto.FiguresRelocationBudget
    _pulling_connections: proto.PullingConnections
    _cells: proto.CellsCache
    _figures: proto.Figures

    @property
    def master(self) -> proto.Master:
        return self._master

    @property
    def figures_budget(self) -> proto.FiguresRelocationBudget:
        return self._figures_budget

    @property
    def pulling_connections(self) -> proto.PullingConnections:
        return self._pulling_connections

    @property
    def board(self) -> proto.Board:
        return self._board

    @property
    def cells(self) -> proto.CellsCache:
        return self._cells

    @property
    def figures(self) -> proto.Figures:
        return self._figures

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self)


def empty_map(*, board_size: int) -> GameSession:
    players = [
        Player(PlayerData(colors.PLAYERS[0], "Red"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[1], "Blue"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[2], "Green"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[3], "Yellow"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[4], "Abobus1"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[5], "Abobus2"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[6], "Abobus3"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYERS[7], "Abobus4"), BotPlayerInputer(BotIgor())),
    ]
    board = Board.from_maker(Vector2Int.ones() * board_size, lambda coord: Cell(MISSING, fig.Water()))
    figures = Figures(board)
    pulling_connections = PullingConnections.make(figures)
    cells = CellsCache(board)
    for cell in board.cells:
        cells.update(cell)

    return GameSession(Master(players), board, FiguresRelocationBudget(), pulling_connections, cells, figures)


def test_map(*, ups: float, board_size: int, initial_town_ratio: float, is_multibot: bool = False) -> GameSession:
    assert 0 <= initial_town_ratio <= 1

    bots_per_frame_thinking_time = .95 / ups
    players = [
        Player(PlayerData(colors.PLAYERS[0], "Red"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[1], "Blue"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[2], "Green"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[3], "Yellow"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[4], "Abobus1"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[5], "Abobus2"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[6], "Abobus3"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYERS[7], "Abobus4"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
    ]
    random.shuffle(players)

    diagonal = board_size * 2 ** .5
    half_size = board_size // 2
    center = Vector2Int.ones() * half_size
    board = Board.from_maker(Vector2Int.ones() * board_size,
                             lambda coord: Cell(((players[0] if coord.x - coord.y <= 0 else players[1])
                                                 if coord.x + coord.y <= diagonal * .7 else
                                                 (players[2] if coord.x - coord.y >= 0 else players[3]))
                                                if (center - coord).length < 18 else
                                                ((players[4] if coord.x - coord.y <= 0 else players[5])
                                                 if coord.x + coord.y <= diagonal * .7 else
                                                 (players[6] if coord.x - coord.y >= 0 else players[7])),
                                                _get_empty_figure(coord, board_size)))

    if not is_multibot:
        players[0].change_inputer(WantsToBeEventPlayerInputer())

    figures = Figures(board)
    pulling_connections = PullingConnections.make(figures)

    cells = CellsCache(board)
    for player in players:
        if not (player_cells := board.cells.with_owner(player).with_figure(fig.Land)):
            continue

        per_player_towns = round(len(player_cells.at_front(board).as_set()) * initial_town_ratio)
        for cell in random.sample(list(player_cells.as_set()), per_player_towns):
            coord = board.coordinates_of(cell)
            figures.add(fig.Town, coord)

    for cell in board.cells:
        cells.update(cell)

    for player in players:
        player.resources.add(Dollars(5_000_000))

    session = GameSession(Master(players), board, FiguresRelocationBudget(), pulling_connections, cells, figures)
    return session


def _get_empty_figure(coord: Vector2Int, board_size: int) -> proto.Figure:
    half_size = board_size // 2
    center = Vector2Int.ones() * half_size

    if (center - coord).length > (half_size - 10):
        return fig.Water()

    if (center - coord).length < 10:
        return fig.Water()

    return fig.Land()
