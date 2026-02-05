import random

from attrs import frozen

import core.protocols as proto
from core.cells_cache import CellsCache
from core.figures.figures import Figures
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots.bot_igor import BotIgor
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


# def test_map(*, board_size: int, initial_town_ratio: float) -> GameSession:
#     assert 0 <= initial_town_ratio <= 1
#
#     players = [
#         Player(PlayerData(colors.PLAYER_RED, "Red"), BotPlayerInputer(BotIgor())),
#         Player(PlayerData(colors.PLAYER_YELLOW, "Yellow"), BotPlayerInputer(BotIgor())),
#         Player(PlayerData(colors.PLAYER_GREEN, "Green"), BotPlayerInputer(BotIgor())),
#         Player(PlayerData(colors.PLAYER_BLUE, "Blue"), BotPlayerInputer(BotIgor())),
#     ]
#     board = Board.from_maker(Vector2Int.ones() * board_size,
#                              lambda coord: Cell((players[3] if coord.y < board_size * .5 else players[2])
#                                                 if coord.x > board_size * .4 else
#                                                 (players[0] if coord.y < board_size * .5 else players[1]),
#                                                 fig.Empty()))
#
#     for player in players:
#         while (len(board.cells.with_owner(player).with_figure(fig.Town).all()) <
#                len(board.cells.with_owner(player).all()) * initial_town_ratio):
#             random.choice(list(board.cells.with_owner(player).with_figure(fig.Empty).all())).insert(fig.Town())
#
#     players[0].resources.add(Dollars(2_000_000))
#     players[1].resources.add(Dollars(2_000_000))
#     players[2].resources.add(Dollars(2_000_000))
#     players[3].resources.add(Dollars(2_000_000))

#     return GameSession(Master(players), board, FiguresRelocationBudget())


def multibot_map(*, ups: float, board_size: int, initial_town_ratio: float) -> GameSession:
    assert 0 <= initial_town_ratio <= 1

    bots_per_frame_thinking_time = .95 / ups
    players = [
        Player(PlayerData(colors.PLAYER_RED, "Red"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYER_YELLOW, "Yellow"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYER_GREEN, "Green"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
        Player(PlayerData(colors.PLAYER_BLUE, "Blue"), BotPlayerInputer(BotIgor(), bots_per_frame_thinking_time)),
    ]
    random.shuffle(players)

    diagonal = board_size * 2 ** .5
    board = Board.from_maker(Vector2Int.ones() * board_size,
                             lambda coord: Cell((players[0] if coord.x - coord.y <= 0 else players[1])
                                                if coord.x + coord.y <= diagonal * .7 else
                                                (players[2] if coord.x - coord.y >= 0 else players[3]),
                                                _get_empty_figure(coord, board_size)))
    random.shuffle(players)

    figures = Figures(board)
    pulling_connections = PullingConnections.make(figures)

    cells = CellsCache(board)
    per_player_towns = round(len(board.cells.with_figure(fig.Land).all()) * initial_town_ratio / len(players))
    for player in players:
        if not (player_cells := board.cells.with_owner(player)):
            continue

        for cell in random.sample(list(player_cells.with_figure(fig.Land).all()), per_player_towns):
            coord = board.coordinates_of(cell)
            figures.add(fig.Town, coord)

    for _ in range(1):
        for cell in board.cells:
            cells.update(cell)

    players[0].resources.add(Dollars(5_000_000))
    players[1].resources.add(Dollars(5_000_000))
    players[2].resources.add(Dollars(5_000_000))
    players[3].resources.add(Dollars(5_000_000))

    return GameSession(Master(players), board, FiguresRelocationBudget(), pulling_connections, cells, figures)


def _get_empty_figure(coord: Vector2Int, board_size: int) -> proto.Figure:
    half_size = board_size // 2
    center = Vector2Int.ones() * half_size
    x, y = coord.tuple
    diagonal = board_size * 2 ** .5

    if (center - coord).length > (half_size - 10):
        return fig.Water()

    if (center - coord).length < 5:
        return fig.Water()

    if abs(x - y) * 2 <= 4:
        return fig.Land()

    if abs(coord.x + coord.y - diagonal * .7) <= 4:
        return fig.Land()

    if (center - coord).length < 13:
        return fig.Land()

    if (center - coord).length < 20:
        return fig.Water()

    return fig.Land()
