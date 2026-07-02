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


def empty_map(*, board_size: int, player_names: list[str]) -> GameSession:
    players = [Player(PlayerData(colors.PLAYERS[index], name), BotPlayerInputer(BotIgor()))
               for index, name in enumerate(player_names)]

    board = Board.from_maker(Vector2Int.ones() * board_size, lambda coord: Cell(MISSING, fig.Water()))
    figures = Figures(board)
    pulling_connections = PullingConnections.make(figures)
    cells = CellsCache(board)
    for cell in board.cells:
        cells.update(cell)

    return GameSession(Master(players), board, FiguresRelocationBudget(), pulling_connections, cells, figures)

