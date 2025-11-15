from types import TracebackType
from time import time, sleep

from attrs import define, field

import core.protocols as proto
from observer import OnEventSubscriber, Event


@define
class PassPlayerInputer(proto.PlayerInputer):
    _move_was_inputted: Event[proto.ValidMove, None] = field(init=False, factory=Event)

    _timeout: float = 0
    _move_start_time: float = field(init=False, default=0)

    @property
    def move_was_inputted(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_inputted.subscriber

    def update(self, session: proto.GameSession) -> None:
        pass

    def wants_to_end_turn(self) -> bool:
        return time() - self._move_start_time >= self._timeout

    def __enter__(self) -> proto.PlayerInputer:
        print("turn started")
        self._move_start_time = time()
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn()
        print("turn ended")
        return None
