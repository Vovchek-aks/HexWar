from types import TracebackType

from attrs import define, field

import core.protocols as proto
from observer import OnEventSubscriber, Event
from statuses import Status, MISSING


@define
class EventPlayerInputer(proto.PlayerInputer):
    _move_was_inputted: Event[proto.ValidMove, None] = field(init=False, factory=Event)

    _wants_to_end_turn: bool = field(init=False, default=False)
    _move_was_read: OnEventSubscriber[proto.ValidMove, None]
    _need_to_end_turn: OnEventSubscriber[None]

    @property
    def move_was_inputted(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_inputted.subscriber

    def update(self, session: proto.GameSession) -> None:
        pass

    def wants_to_end_turn(self) -> bool:
        return self._wants_to_end_turn

    def _make_want_end_turn(self) -> None:
        self._wants_to_end_turn = True

    def __enter__(self) -> proto.PlayerInputer:
        self._wants_to_end_turn = False
        self._need_to_end_turn.subscribe(self._make_want_end_turn)
        self._move_was_read.subscribe(self._move_was_inputted.invoke)
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn() or not issubclass(exc_type, Exception)

        self._need_to_end_turn.unsubscribe(self._make_want_end_turn)
        self._move_was_read.unsubscribe(self._move_was_inputted.invoke)
        return None


@define
class EventPlayerInputerBuilder:
    _move_was_read: OnEventSubscriber[proto.ValidMove, None] | Status = MISSING
    _need_to_end_turn: OnEventSubscriber[None] | Status = MISSING

    def is_valid(self) -> bool:
        return MISSING not in (self._move_was_read, self._need_to_end_turn)

    def build(self) -> EventPlayerInputer:
        assert self.is_valid()
        return EventPlayerInputer(self._move_was_read, self._need_to_end_turn)

    def set_move_was_read(self,
                          move_was_read: OnEventSubscriber[proto.ValidMove, None]) -> "EventPlayerInputerBuilder":
        self._move_was_read = move_was_read
        return self

    def set_need_to_end_turn(self, need_to_end_turn: OnEventSubscriber[None]) -> "EventPlayerInputerBuilder":
        self._need_to_end_turn = need_to_end_turn
        return self
