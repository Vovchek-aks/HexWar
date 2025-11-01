from attrs import define

import core.protocols as proto
from core.figures import figures as fig
from statuses import MISSING


@define(eq=False)
class Cell(proto.Cell):
    _owner: proto.Player
    _figure: proto.Figure

    @property
    def owner(self) -> proto.Player:
        return self._owner

    @property
    def figure(self) -> proto.Figure:
        return self._figure

    @property
    def is_empty(self) -> bool:
        return isinstance(self.figure, fig.Empty)

    def hardness(self, board: proto.Board) -> int:
        assert board.has(self)

        coord = board.coordinates_of(self)
        return max(cell.figure.hardness(coord, board)
                   for cell in board.get_neighbors(self, include_cell=True).with_owner(self.owner))

    def strength(self, board: proto.Board, *, strict: bool = True) -> int:
        assert board.has(self)

        if (movable := self.figure.FLAGS.get(proto.Movable)) is MISSING and not strict:
            return 0

        assert movable is not MISSING

        coord = board.coordinates_of(self)
        return movable.strength(coord, board)

    def pop(self) -> proto.Figure:
        assert not self.is_empty

        figure = self.figure
        self._figure = fig.Empty()
        return figure

    def insert(self, figure: proto.Figure) -> None:
        assert self.is_empty

        self._figure = figure

    def take_from(self, other: proto.Cell) -> None:
        self._owner = other.owner
        self._figure = other.pop()

    def __eq__(self, other: proto.Cell) -> bool:
        return self is other
