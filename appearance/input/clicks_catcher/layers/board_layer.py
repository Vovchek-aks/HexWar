from attrs import frozen, field

import appearance.protocols as proto
from mathematics.vector import Vector2Int
from observer import Event, ToEventSubscriber
from statuses import MISSING


@frozen
class BoardLayer(proto.ClicksCatchingLayer):
    _cell_getter: proto.SelectedCellGetter
    _cell_was_clicked: Event[Vector2Int, None] = field(init=False, factory=Event)

    @property
    def cell_was_clicked(self) -> ToEventSubscriber[Vector2Int, None]:
        return self._cell_was_clicked.subscriber

    def can_catch(self, click: proto.Click) -> bool:
        return self._cell_getter.get_coord(click.screen_position) is not MISSING

    def catch(self, click: proto.Click) -> None:
        assert self.can_catch(click)

        cell_coord = self._cell_getter.get_coord(click.screen_position)
        self._cell_was_clicked.invoke(cell_coord)
