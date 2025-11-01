from attrs import frozen

import core.protocols as proto
from appearance.graphics import colors
from core.board import Board
from core.cell import Cell
from core.player import Player
from mathematics.vector import Vector2Int
import core.figures.figures as fig


@frozen
class GameSession(proto.GameSession):
    @classmethod
    def test_map(cls, *, board_size: int) -> "proto.GameSession":
        player1 = Player(colors.PLAYER_RED)
        player2 = Player(colors.PLAYER_BLUED)
        player3 = Player(colors.PLAYER_GREEN)
        player4 = Player(colors.PLAYER_YELLOW)
        board = Board.from_maker(Vector2Int.ones() * board_size,
                                 lambda coord: Cell((player2 if coord.y < board_size * .4 else player3)
                                                    if coord.x > board_size * .3 else
                                                    (player1 if coord.y < board_size * .6 else player4),
                                                    fig.Empty()))

        board[Vector2Int(0, 0)].insert(fig.Infantry())
        board[Vector2Int(1, 0)].insert(fig.Infantry())
        board[Vector2Int(0, 1)].insert(fig.Tank())
        board[Vector2Int(5, 7)].insert(fig.Artillery())
        board[Vector2Int(5, 8)].insert(fig.Infantry())
        board[Vector2Int(2, 8)].insert(fig.Motorization())
        board[Vector2Int(7, 2)].insert(fig.Bunker())

        return cls(..., [player1, player2, player3, player4], board)

    _master: proto.Master
    _players: list[proto.Player]
    _board: proto.Board

    @property
    def master(self) -> proto.Master:
        return self.master

    @property
    def board(self) -> proto.Board:
        return self._board
