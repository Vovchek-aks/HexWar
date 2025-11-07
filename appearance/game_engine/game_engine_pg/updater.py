from attrs import frozen

from appearance.game_engine.game_engine_pg.user_input import UserInput
from appearance.input.camera_mover import CameraMover
from appearance.input.clicks_catcher import ClicksCatcher
from appearance.layer import Layer


@frozen
class Updater:
    @classmethod
    def make(cls, camera_mover: CameraMover, layers: list[Layer]) -> "Updater":
        clicks_catcher = ClicksCatcher(layers)
        return cls(camera_mover,
                   clicks_catcher)

    _camera_mover: CameraMover
    _clicks_catcher: ClicksCatcher

    def update(self, user_input: UserInput) -> None:
        self._camera_mover.update(user_input.events, user_input.keys, user_input.dt)
        self._clicks_catcher.update(user_input.events, user_input.mouse_position)
