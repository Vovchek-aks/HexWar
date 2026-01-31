from attrs import frozen, field

import core.protocols as proto
from core.protocols import Empty
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
import core.figures.figure as fig


@frozen
class Figures(proto.Figures):
    _board: proto.Board
    _coord_of: dict[fig.Figure, Vector2Int] = field(init=False, factory=dict)

    _figure_was_added: Event[fig.Figure, Vector2Int, None] = field(init=False, factory=Event)
    _figure_was_removed: Event[fig.Figure, Vector2Int, None] = field(init=False, factory=Event)
    _figure_was_moved: Event[fig.Figure, Vector2Int, Vector2Int, None] = field(init=False, factory=Event)
    _figure_was_converted: Event[fig.Figure, fig.Figure, Vector2Int, None] = field(init=False, factory=Event)

    @property
    def figure_was_added_at(self) -> OnEventSubscriber[fig.Figure, Vector2Int, None]:
        return self._figure_was_added.subscriber

    @property
    def figure_was_removed(self) -> OnEventSubscriber[fig.Figure, Vector2Int, None]:
        return self._figure_was_removed.subscriber

    @property
    def figure_was_moved(self) -> OnEventSubscriber[fig.Figure, Vector2Int, Vector2Int, None]:
        return self._figure_was_moved.subscriber

    @property
    def figure_was_converted(self) -> OnEventSubscriber[fig.Figure, fig.Figure, Vector2Int, None]:
        return self._figure_was_converted.subscriber

    def locate(self, figure: fig.Figure) -> Vector2Int:
        assert figure in self._coord_of

        return self._coord_of[figure]

    def add(self, figure_type: type[fig.Figure], coord: Vector2Int) -> None:
        assert Empty not in figure_type.FLAGS

        cell = self._board[coord]
        assert cell.is_empty

        figure = figure_type()
        self._coord_of[figure] = coord
        cell.insert(figure)

        self._figure_was_added.invoke(figure, coord)

    def remove_at(self, coord: Vector2Int) -> None:
        figure = self._board[coord].figure
        self.remove(figure)

    def remove(self, figure: fig.Figure) -> None:
        assert figure in self._coord_of

        coord = self._coord_of[figure]
        cell = self._board[coord]
        assert not cell.is_empty

        self._coord_of.pop(figure)
        cell.pop()

        self._figure_was_removed.invoke(figure, coord)

    def move(self, figure: fig.Figure, target: Vector2Int) -> None:
        assert figure in self._coord_of

        target_cell = self._board[target]
        assert target_cell.is_empty

        coord = self._coord_of[figure]
        cell = self._board[coord]

        self._coord_of[figure] = target
        target_cell.take_from(cell)
        self._figure_was_moved.invoke(figure, coord, target)

    def convert(self, figure: fig.Figure, target_type: type[fig.Figure]) -> None:
        assert figure in self._coord_of
        assert Empty not in target_type.FLAGS

        coord = self._coord_of[figure]
        cell = self._board[coord]

        target = target_type()
        self._coord_of.pop(figure)
        self._coord_of[target] = coord
        cell.pop()
        cell.insert(target)

        self._figure_was_converted.invoke(figure, target, coord)
