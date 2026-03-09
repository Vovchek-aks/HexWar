from my_types import TracebackType

from attrs import frozen
import pygame as pg

from appearance.game_engine.game_engine_pg.events import UpdatableEvents
from appearance.game_engine.game_engine_pg.frame_drawer import FrameDrawer
from appearance.game_engine.game_engine_pg.timer import Timer
from appearance.game_engine.game_engine_pg.updater import Updater
from appearance.game_engine.game_engine_pg.user_input import UserInput


@frozen
class GameEngine:
    _caption: str
    _timer: Timer
    _drawer: FrameDrawer
    _updater: Updater
    _last_frame_events: UpdatableEvents

    def run(self) -> None:
        while not self.need_to_stop():
            self.update()

    def update(self) -> None:
        user_input = UserInput.read(self._last_frame_events, self._timer)

        self._updater.update(user_input)

        self._drawer.draw_frame(user_input.mouse_position)
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
