from attrs import define

import appearance.protocols as proto


@define
class GameScene:
    _drawer: proto.FrameDrawer
    _updater: proto.Updater
    _input_state: proto.InputState

    def update(self) -> None:
        self._updater.update(self._input_state)

    def draw(self) -> None:
        self._drawer.draw_frame(self._input_state.mouse_position)
