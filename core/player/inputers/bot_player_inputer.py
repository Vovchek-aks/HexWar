from types import TracebackType

from attrs import define, field

import core.protocols as proto
from observer import OnEventSubscriber, Event


@define
class BotPlayerInputer(proto.PlayerInputer):
    bot: type[proto.Bot]

    _move_was_inputted: Event[proto.ValidMove, None] = field(init=False, factory=Event)

    _wants_to_end_turn: bool = field(init=False, default=False)

    @property
    def move_was_inputted(self) -> OnEventSubscriber[proto.ValidMove, None]:
        return self._move_was_inputted.subscriber

    def wants_to_end_turn(self) -> bool:
        return self._wants_to_end_turn

    def update(self, session: proto.GameSession) -> None:
        bot = self.bot.make(session, self._move_was_inputted)
        self._wants_to_end_turn = bot.update()

    def __enter__(self) -> proto.PlayerInputer:
        self._wants_to_end_turn = False
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn() or not issubclass(exc_type, Exception)
        return None
