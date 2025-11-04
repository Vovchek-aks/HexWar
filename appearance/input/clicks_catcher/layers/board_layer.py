from attrs import frozen, field

import appearance.protocols as proto
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import MISSING


@frozen
class BoardLayer(proto.BoardLayer):
    _cell_getter: proto.UnderCursorCellGetter

    _cell_was_clicked_left: Event[Vector2Int, None] = field(init=False, factory=Event)
    _cell_was_clicked_right: Event[Vector2Int, None] = field(init=False, factory=Event)
    _cell_was_clicked_middle: Event[Vector2Int, None] = field(init=False, factory=Event)

    @property
    def cell_was_clicked_left(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_was_clicked_left.subscriber

    @property
    def cell_was_clicked_right(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_was_clicked_right.subscriber

    @property
    def cell_was_clicked_middle(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_was_clicked_middle.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return self._cell_getter.get_coord(click.screen_position) is not MISSING

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        cell_coord = self._cell_getter.get_coord(click.screen_position)

        if click.is_left:
            self._cell_was_clicked_left.invoke(cell_coord)

        if click.is_right:
            self._cell_was_clicked_right.invoke(cell_coord)

        if click.is_middle:
            self._cell_was_clicked_middle.invoke(cell_coord)
