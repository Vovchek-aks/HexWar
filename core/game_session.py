import random

from attrs import frozen

import core.protocols as proto
from core.cells import Cells
from core.cells_cache import CellsCache
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.bots.bot_igor import BotIgor
from core.resources import Dollars
from mathematics.vector import Vector2Int
from appearance.graphics import colors
from core.board import Board
from core.cell import Cell
from core.figures.figures_relocation_budget import FiguresRelocationBudget
from core.master import Master
from core.player import PlayerData, Player
import core.figures.figures as fig


@frozen
class GameSession(proto.GameSession):
    _master: proto.Master
    _board: proto.Board
    _figures_budget: proto.FiguresRelocationBudget
    _cells: proto.CellsCache

    @property
    def master(self) -> proto.Master:
        return self._master

    @property
    def figures_budget(self) -> proto.FiguresRelocationBudget:
        return self._figures_budget

    @property
    def board(self) -> proto.Board:
        return self._board

    @property
    def cells(self) -> proto.CellsCache:
        return self._cells

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


def multibot_map(*, board_size: int, initial_town_ratio: float) -> GameSession:
    assert 0 <= initial_town_ratio <= 1

    players = [
        Player(PlayerData(colors.PLAYER_RED, "Red"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYER_YELLOW, "Yellow"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYER_GREEN, "Green"), BotPlayerInputer(BotIgor())),
        Player(PlayerData(colors.PLAYER_BLUE, "Blue"), BotPlayerInputer(BotIgor())),
    ]
    random.shuffle(players)

    diagonal = board_size * 2 ** .5
    board = Board.from_maker(Vector2Int.ones() * board_size,
                             lambda coord: Cell((players[0] if coord.x - coord.y <= 0 else players[1])
                                                if coord.x + coord.y <= diagonal * .7 else
                                                (players[2] if coord.x - coord.y >= 0 else players[3]),
                                                fig.Empty()))
    random.shuffle(players)

    cells = CellsCache(board)
    per_player_towns = round(board_size ** 2 * initial_town_ratio / len(players))
    for player in players:
        if not (player_cells := board.cells.with_owner(player)):
            continue

        for cell in random.sample(list(player_cells.all()), per_player_towns):
            cell.insert(fig.Town())

    for _ in range(1):
        for cell in board.cells:
            cells.update(cell)

    players[0].resources.add(Dollars(5_000_000))
    players[1].resources.add(Dollars(5_000_000))
    players[2].resources.add(Dollars(5_000_000))
    players[3].resources.add(Dollars(5_000_000))

    return GameSession(Master(players), board, FiguresRelocationBudget(), cells)
