from attrs import frozen

import core.protocols as proto


@frozen
class ValidMove(proto.ValidMove):
    _move: proto.Move

    @property
    def move(self) -> proto.Move:
        return self._move
