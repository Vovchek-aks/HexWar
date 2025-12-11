from attrs import frozen

import core.protocols as proto
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

    @property
    def master(self) -> proto.Master:
        return self._master

    @property
    def figures_budget(self) -> proto.FiguresRelocationBudget:
        return self._figures_budget

    @property
    def board(self) -> proto.Board:
        return self._board

    def make(self, move: proto.ValidMove) -> None:
        move.move.execute(self)


def test_map(*, board_size: int) -> GameSession:
    players = [
        Player(PlayerData(colors.PLAYER_RED, "Red"), BotPlayerInputer(BotIgor)),
        Player(PlayerData(colors.PLAYER_YELLOW, "Yellow"), BotPlayerInputer(BotIgor)),
        Player(PlayerData(colors.PLAYER_GREEN, "Green"), BotPlayerInputer(BotIgor)),
        Player(PlayerData(colors.PLAYER_BLUE, "Blue"), BotPlayerInputer(BotIgor)),
    ]
    board = Board.from_maker(Vector2Int.ones() * board_size,
                             lambda coord: Cell((players[3] if coord.y < board_size * .5 else players[2])
                                                if coord.x > board_size * .4 else
                                                (players[0] if coord.y < board_size * .5 else players[1]),
                                                fig.Empty()))

    # board[Vector2Int(0, 0)].insert(fig.Infantry())
    # board[Vector2Int(1, 0)].insert(fig.Infantry())
    # board[Vector2Int(1, 3)].insert(fig.Infantry())
    # board[Vector2Int(0, 1)].insert(fig.Tank())

    # board[Vector2Int(1, 4)].insert(fig.Tank())
    # board[Vector2Int(5, 7)].insert(fig.Town())

    # board[Vector2Int(5, 8)].insert(fig.Infantry())
    # board[Vector2Int(2, 8)].insert(fig.Town())

    # board[Vector2Int(9, 2)].insert(fig.Town())
    # board[Vector2Int(7, 2)].insert(fig.Bunker())
    # board[Vector2Int(6, 2)].insert(fig.Infantry())

    players[0].resources.add(Dollars(2_000_000))
    players[1].resources.add(Dollars(2_000_000))
    players[2].resources.add(Dollars(2_000_000))
    players[3].resources.add(Dollars(2_000_000))

    return GameSession(Master(players), board, FiguresRelocationBudget())
