from my_types import TracebackType

from attrs import define, field

import appearance.protocols as proto
from appearance.scenes.game_scene import GameScene
from appearance.scenes.pause_menu import PauseMenu
from observer import Event, OnEventSubscriber
from statuses import Status, MISSING


@define
class GameWithPauseScene(proto.SceneWithSwitchTo):
    _game: GameScene
    _pause_menu: PauseMenu

    _is_paused: bool = False
    _next_scene: proto.Scene | Status = field(init=False, default=MISSING)

    _was_switched: Event[proto.Scene, None] = field(init=False, factory=Event)

    @property
    def was_switched(self) -> OnEventSubscriber[proto.Scene, None]:
        return self._was_switched.subscriber

    def next(self) -> proto.Scene | Status:
        return self._next_scene

    def update(self) -> None:
        if self._is_paused:
            self._pause_menu.update()
            return
        self._game.update()

    def draw(self) -> None:
        self._game.draw()
        if self._is_paused:
            self._pause_menu.draw()

    def on_pause_menu_toggle_requested(self) -> None:
        self._is_paused = not self._is_paused

    def switch_to(self, scene: proto.Scene) -> None:
        self._next_scene = scene
        self._was_switched.invoke(scene)

    def __enter__(self) -> proto.Scene:
        return self

    def __exit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> bool | None:
        return None
