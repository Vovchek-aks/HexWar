from abc import ABC
from typing import Callable

from attrs import frozen

import protocols as proto
import figures as fig
from vector import Vector2Int


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
    def validate(self, board: proto.Board) -> proto.ValidMove | proto.INVALID:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]

        if from_cell.owner == to_cell.owner:
            return proto.INVALID

        if not isinstance(movable := from_cell.figure, proto.MovableFigure):
            return proto.INVALID

        if movable.STRENGTH == fig.MAX_STRENGTH:
            return ValidMove(self)

        if movable.STRENGTH <= to_cell.strength:
            return proto.INVALID

        return ValidMove(self)


@frozen
class Relocation(_FiguresRelocation):
    def validate(self, board: proto.Board) -> proto.ValidMove | proto.INVALID:
        from_cell = board[self.from_coord]
        to_cell = board[self.to_coord]

        if from_cell.owner != to_cell.owner:
            return proto.INVALID

        if not isinstance(from_cell.figure, proto.MovableFigure):
            return proto.INVALID

        if not isinstance(to_cell.figure, fig.Empty | fig.Tree):
            return proto.INVALID

        return ValidMove(self)


@frozen
class Creation(proto.Move):
    create_figure: Callable[[], proto.CreatableFigure]
    to_coord: Vector2Int

    def validate(self, board: proto.Board) -> proto.ValidMove | proto.INVALID:
        to_cell = board[self.to_coord]

        if not to_cell.is_empty:
            return proto.INVALID

        return ValidMove(self)

    def execute(self, board: proto.Board) -> None:
        board[self.to_coord].insert(self.create_figure())
