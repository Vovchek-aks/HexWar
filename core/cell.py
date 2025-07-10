from attrs import define

import core.protocols as proto
from core.figures import figures as fig


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

    def strength(self, board: proto.Board) -> int:
        assert board.has_cell(self)

        return max(cell.figure.STRENGTH for cell in board.get_neighbors(self, include_cell=True))

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
