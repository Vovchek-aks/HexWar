from abc import ABC
from typing import Callable

from attrs import frozen

import protocols as proto
from core.figures import figures as fig
import core.figures.figures_flags as flags
from vector import Vector2Int
from statuses import Status, INVALID


@frozen
class ValidMove(proto.ValidMove):
    _move: proto.Move

    @property
    def move(self) -> proto.Move:
        return self._move


@frozen
class _FiguresRelocation(proto.Move, ABC):
    from_coord: Vector2Int
    to_coord: Vector2Int

    def execute(self, board: proto.Board) -> None:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]
        to_cell.take_from(from_cell)


@frozen
class Capture(_FiguresRelocation):
    def validate(self, board: proto.Board) -> proto.ValidMove | Status:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]

        if from_cell.owner == to_cell.owner:
            return INVALID

        if flags.Movable not in (movable := from_cell.figure).FLAGS:
            return INVALID

        if movable.STRENGTH == fig.MAX_STRENGTH:
            return ValidMove(self)

        if movable.STRENGTH <= to_cell.strength(board):
            return INVALID

        return ValidMove(self)


@frozen
class Relocation(_FiguresRelocation):
    def validate(self, board: proto.Board) -> proto.ValidMove | Status:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]

        if from_cell.owner != to_cell.owner:
            return INVALID

        if flags.Movable not in from_cell.figure.FLAGS:
            return INVALID

        if not isinstance(to_cell.figure, fig.Empty | fig.Tree):
            return INVALID

        return ValidMove(self)


@frozen
class Creation(proto.Move):
    create_figure: Callable[[], proto.Figure] | type[proto.Figure]
    to_coord: Vector2Int

    def validate(self, board: proto.Board) -> proto.ValidMove | Status:
        to_cell = board[self.to_coord]

        if not to_cell.is_empty:
            return INVALID

        return ValidMove(self)

    def execute(self, board: proto.Board) -> None:
        figure = self.create_figure()
        assert flags.Creatable in figure.FLAGS

        board[self.to_coord].insert(figure)
