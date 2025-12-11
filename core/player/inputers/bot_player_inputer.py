from types import TracebackType

from attrs import define, field

import core.protocols as proto
from statuses import Status, MISSING


@define
class BotPlayerInputer(proto.PlayerInputer):
    _bot_type: type[proto.Bot]

    _bot: proto.Bot | Status = field(init=False, default=MISSING)
    _wants_to_end_turn: bool = field(init=False, default=False)

    def wants_to_end_turn(self) -> bool:
        return self._wants_to_end_turn

    def get_move(self, session: proto.GameSession) -> proto.ValidMove | Status:
        assert self._bot is not MISSING

        move = self._bot.get_move(session)
        if move is MISSING:
            self._wants_to_end_turn = True
        return move

    def __enter__(self) -> proto.PlayerInputer:
        self._bot = self._bot_type.make()
        self._wants_to_end_turn = False
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn() or not issubclass(exc_type, Exception)
        self._bot = MISSING
        return None
