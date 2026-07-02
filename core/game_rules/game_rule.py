from abc import ABCMeta
from typing import Iterator

import core.protocols as proto


class GameRule(proto.GameRule, metaclass=ABCMeta):
    def on_turn_start(self, session: proto.GameSession) -> Iterator[None]:
        yield

    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        yield
