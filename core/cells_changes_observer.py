from attrs import frozen, field

import core.protocols as proto
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber


@frozen
class CellsChangesObserver(proto.CellsChangesObserver):
    @classmethod
    def make(cls,
             cell_changed_owner_events: list[OnEventSubscriber[Vector2Int, None]],
             cell_changed_figure_events: list[OnEventSubscriber[Vector2Int, None]]) -> "CellsChangesObserver":
        self = cls()
        for event in cell_changed_owner_events:
            event.subscribe(self._cell_changed_owner.invoke)
        for event in cell_changed_figure_events:
            event.subscribe(self._cell_changed_figure.invoke)
        return self

    _cell_changed_owner: Event[Vector2Int, None] = field(init=False, factory=Event)
    _cell_changed_figure: Event[Vector2Int, None] = field(init=False, factory=Event)

    @property
    def cell_changed_owner(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_owner.subscriber

    @property
    def cell_changed_figure(self) -> OnEventSubscriber[Vector2Int, None]:
        return self._cell_changed_figure.subscriber
