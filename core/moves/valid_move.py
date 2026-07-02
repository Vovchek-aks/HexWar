from attrs import frozen

import core.protocols as proto


@frozen
class ValidMove[T: proto.Move](proto.ValidMove):
    _move: T

    @property
    def move(self) -> T:
        return self._move
