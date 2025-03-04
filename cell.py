from attrs import define

import protocols as proto
import figures as fig


@define
class Cell(proto.Cell):
    _controlling: proto.Agent
    _figure: proto.Figure

    @property
    def controlling(self) -> proto.Agent:
        return self._controlling

    @property
    def figure(self) -> proto.Figure:
        return self._figure

    def pop_figure(self) -> proto.Figure:
        figure = self.figure
        self._figure = fig.Empty()
        return figure

    def take_from(self, other: "Cell") -> None:
        assert isinstance(other.figure, proto.FigureMovable)

        self._controlling = other.controlling
        self._figure = other.pop_figure()
