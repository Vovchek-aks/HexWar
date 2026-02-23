from types import TracebackType

from attrs import define

import core.protocols as proto
from statuses import Status


@define
class WantsToBeEventPlayerInputer(proto.PlayerInputer):
    def get_move(self, session: proto.GameSession) -> proto.ValidMove | Status:
        assert False

    def wants_to_end_turn(self) -> bool:
        assert False

    def __enter__(self) -> proto.PlayerInputer:
        assert False

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        assert False
