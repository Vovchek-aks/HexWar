from attrs import frozen

import appearance.protocols as proto


@frozen
class MouseButtons(proto.MouseButtons):
    _is_left: bool = False
    _is_right: bool = False
    _is_middle: bool = False

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def is_right(self) -> bool:
        return self._is_right

    @property
    def is_middle(self) -> bool:
        return self._is_middle
