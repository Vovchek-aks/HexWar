from attrs import frozen

import core.protocols as proto
from mathematics.vector import Vector2Int
from appearance.graphics import colors
from core.board import Board
from core.cell import Cell
from core.figures.figures_budget import FiguresBudget
from core.master import Master
from core.player import PlayerData, Player, PassPlayerInputer
import core.figures.figures as fig


@frozen
class GameSession(proto.GameSession):
    _master: proto.Master
    _board: proto.Board
    _figures_budget: proto.FiguresBudget

    @property
    def master(self) -> proto.Master:
        return self._master

    @property
    def figures_budget(self) -> proto.FiguresBudget:
        return self._figures_budget

    @property
    def board(self) -> proto.Board:
        return self._board

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self)


def test_map(*, board_size: int) -> GameSession:
    players = [
        Player(PlayerData(colors.PLAYER_RED, "Red"), PassPlayerInputer()),
        Player(PlayerData(colors.PLAYER_YELLOW, "Yellow"), PassPlayerInputer(1)),
        Player(PlayerData(colors.PLAYER_GREEN, "Green"), PassPlayerInputer(1)),
        Player(PlayerData(colors.PLAYER_BLUE, "Blue"), PassPlayerInputer(1)),
    ]
    board = Board.from_maker(Vector2Int.ones() * board_size,
                             lambda coord: Cell((players[3] if coord.y < board_size * .4 else players[2])
                                                if coord.x > board_size * .3 else
                                                (players[0] if coord.y < board_size * .6 else players[1]),
                                                fig.Empty()))

    board[Vector2Int(0, 0)].insert(fig.Infantry())
    board[Vector2Int(1, 0)].insert(fig.Infantry())
    board[Vector2Int(1, 1)].insert(fig.Infantry())
    board[Vector2Int(0, 1)].insert(fig.Tank())
    board[Vector2Int(5, 7)].insert(fig.Artillery())
    board[Vector2Int(5, 8)].insert(fig.Infantry())
    board[Vector2Int(2, 8)].insert(fig.Motorization())
    board[Vector2Int(7, 2)].insert(fig.Bunker())
    board[Vector2Int(6, 2)].insert(fig.Infantry())

    return GameSession(Master(players), board, FiguresBudget())
