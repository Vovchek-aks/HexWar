from types import TracebackType
from time import time

from attrs import define, field

import core.protocols as proto
from statuses import Status, MISSING


@define
class PassPlayerInputer(proto.PlayerInputer):
    _timeout: float = 0
    _move_start_time: float = field(init=False, default=0)

    def get_move(self, session: proto.GameSession) -> proto.ValidMove | Status:
        return MISSING

    def wants_to_end_turn(self) -> bool:
        return time() - self._move_start_time >= self._timeout

    def __enter__(self) -> proto.PlayerInputer:
        self._move_start_time = time()
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn() or not issubclass(exc_type, Exception)
        return None
