from my_types import TracebackType
from time import time

from attrs import define, field

import core.protocols as proto
from statuses import Status, MISSING, IN_PROGRESS

THINK_TIME_RATIO = .8


@define
class BotPlayerInputer(proto.PlayerInputer):
    _bot: proto.Bot
    _ups: float = 0

    _wants_to_end_turn: bool = field(init=False, default=False)

    @property
    def bot(self) -> proto.Bot:
        return self._bot

    @property
    def time_to_think(self) -> float:
        return THINK_TIME_RATIO / self._ups

    def wants_to_end_turn(self) -> bool:
        return self._wants_to_end_turn

    def get_move(self, session: proto.GameSession) -> proto.ValidMove | Status:
        assert self._bot is not MISSING

        start_thinking = time()
        while (move := self._bot.get_move(session)) is IN_PROGRESS:
            thinking_time = time() - start_thinking
            if thinking_time >= self.time_to_think:
                break

        if move is MISSING:
            self._wants_to_end_turn = True
        return move

    def __enter__(self) -> proto.PlayerInputer:
        self._wants_to_end_turn = False
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert self.wants_to_end_turn() or not issubclass(exc_type, Exception)
        return None
