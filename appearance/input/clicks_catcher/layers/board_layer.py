from attrs import frozen, field

import appearance.protocols as proto
from appearance.input.clicks_catcher.click import MouseButtons
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import MISSING


@frozen
class BoardLayer(proto.BoardLayer):
    _cell_getter: proto.UnderCursorCellGetter

    _cell_was_clicked: Event[Vector2Int, MouseButtons, None] = field(init=False, factory=Event)
    _was_clicked: Event[proto.Click, None] = field(init=False, factory=Event)

    @property
    def cell_was_clicked(self) -> OnEventSubscriber[Vector2Int, MouseButtons, None]:
        return self._cell_was_clicked.subscriber

    @property
    def was_clicked(self) -> OnEventSubscriber[proto.Click, None]:
        return self._was_clicked.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return self._cell_getter.get_coord(click.screen_position) is not MISSING

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        self._was_clicked.invoke(click)

        cell_coord = self._cell_getter.get_coord(click.screen_position)
        self._cell_was_clicked.invoke(cell_coord, click.buttons)
