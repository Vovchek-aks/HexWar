from attrs import define

import protocols as proto
import figures as fig


@define
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

    @property
    def strength(self) -> int:
        return self.figure.STRENGTH  # todo: add projected

    def pop(self) -> proto.Figure:
        figure = self.figure
        self._figure = fig.Empty()
        return figure

    def insert(self, figure: proto.Figure) -> None:
        assert self.is_empty

        self._figure = figure

    def take_from(self, other: "Cell") -> None:
        self._owner = other.owner
        self._figure = other.pop()
