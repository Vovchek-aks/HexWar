from typing import Callable

from attrs import frozen, define

import core.protocols as proto
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
from statuses import Status, MISSING

_CELL_WAS_POPPED = Event[Vector2Int, None]()


@frozen
class UpdatableOnTurnStart(proto.UpdatableOnTurnStart):
    EXCLUDES = set[type[proto.Flag]]()

    @classmethod
    def cell_was_popped(cls) -> OnEventSubscriber[Vector2Int, None]:
        return _CELL_WAS_POPPED.subscriber

    _update: Callable[[Vector2Int, proto.GameSession], None]

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        self._update(coord, session)


@define
class UpdatableOnTurnStartBuilder:
    _update: Callable[[Vector2Int, proto.GameSession], None] | Status = MISSING

    def is_valid(self) -> bool:
        return MISSING not in (self._update,)

    def build(self) -> UpdatableOnTurnStart:
        assert self.is_valid()
        return UpdatableOnTurnStart(self._update)

    def set_update(self,
                   update: Callable[[Vector2Int, proto.GameSession], None]) -> "UpdatableOnTurnStartBuilder":
        self._update = update
        return self

    def add_resources(self, resource: proto.Resource) -> "UpdatableOnTurnStartBuilder":
        return self.set_update(lambda _, session: session.master.current_player.resources.add(resource))

    def try_take_else_die(self, resource: proto.Resource) -> "UpdatableOnTurnStartBuilder":
        def update(coord: Vector2Int, session: proto.GameSession) -> None:
            resources = session.master.current_player.resources
            if resources.can_take(resource):
                resources.take(resource)
                return
            session.board[coord].pop()
            _CELL_WAS_POPPED.invoke(coord)

        return self.set_update(update)
