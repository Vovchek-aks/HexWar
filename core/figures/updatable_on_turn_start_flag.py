from typing import Callable

from attrs import frozen, define

import core.protocols as proto
from mathematics.vector import Vector2Int
from statuses import Status, MISSING


@frozen
class UpdatableOnTurnStart(proto.UpdatableOnTurnStart):
    EXCLUDES = set[type[proto.Flag]]()

    _update: Callable[[Vector2Int, proto.GameSession], None]

    def update(self, coord: Vector2Int, session: proto.GameSession) -> None:
        self._update(coord, session)
