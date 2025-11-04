from types import TracebackType

from attrs import frozen
import pygame as pg

from appearance.game_engine.game_engine_pg.events import UpdatableEvents
from appearance.game_engine.game_engine_pg.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_pg.timer import Timer
from appearance.input.camera_mover import CameraMover
from appearance.input.clicks_catcher import ClicksCatcher
from mathematics.vector import Vector2


@frozen
class GameEngine:
    _caption: str
    _timer: Timer
    _drawer: FrameDrawer
    _camera_mover: CameraMover
    _clicks_catcher: ClicksCatcher
    _last_frame_events: UpdatableEvents

    def run(self) -> None:
        while not self.need_to_stop():
            self.update()

    def update(self) -> None:
        events = self._last_frame_events.get()
        keys = pg.key.get_pressed()
        mouse_position = Vector2(*pg.mouse.get_pos())

        self._camera_mover.update(events, keys, self._timer.dt)
        self._clicks_catcher.update(events, mouse_position)

        self._drawer.draw_frame(mouse_position)
        self._timer.tick()

        pg.display.set_caption(f"{self._caption} {1 / self._timer.dt:.0f}FPS")

        self._last_frame_events.read()

    def need_to_stop(self) -> bool:
        return pg.QUIT in self._last_frame_events.get()

    def __enter__(self) -> "GameEngine":
        return self

    def __exit__(self,
                 exc_type: type[BaseException],
                 exc_val: BaseException,
                 exc_tb: TracebackType) -> bool | None:
        pg.quit()
        return None
