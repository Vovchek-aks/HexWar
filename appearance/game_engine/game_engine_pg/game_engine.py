from attrs import define
import pygame as pg

from appearance.graphics.camera.camera import Camera
from appearance.graphics.camera.camera_orientation import CameraOrientation
from appearance.graphics.drawer import Draw
from appearance.input.camera_mover import CameraMover
from appearance.input.selected_cell_getter import SelectedCellGetter
from appearance.game_engine.game_engine_pg.events import Events
from core.protocols import GameSession
from mathematics.vector import Vector2Int, Vector2
from statuses import MISSING


@define
class GameEngine:
    @classmethod
    def start(cls, caption: str, ups: int, screen_shape: Vector2Int, session: GameSession) -> "GameEngine":
        pg.init()
        screen = pg.display.set_mode(screen_shape.tuple)
        pg.display.set_caption(caption)
        clock = pg.time.Clock()

        camera_orientation = CameraOrientation.starter()
        camera_mover = CameraMover(camera_orientation)
        camera = Camera(screen_shape, camera_orientation)

        selected_cell_getter = SelectedCellGetter(camera, session.board)

        draw = Draw(screen, camera, session.board)

        dt = 1 / ups

        return cls(ups, dt, caption, clock, draw, selected_cell_getter, camera_mover, Events.read())

    _ups: int
    _dt: float
    _caption: str
    _clock: pg.time.Clock
    _draw: Draw
    _selected_cell_getter: SelectedCellGetter
    _camera_mover: CameraMover
    _last_frame_events: Events

    def update(self) -> None:
        keys = pg.key.get_pressed()
        mouse_position = Vector2(*pg.mouse.get_pos())

        self._camera_mover.update(self._last_frame_events, keys, self._dt)

        self._draw.background()
        self._draw.board()

        if (selected_coord := self._selected_cell_getter.get_coord(mouse_position)) is not MISSING:
            self._draw.highlighted(selected_coord)

        pg.display.flip()
        dt = self._clock.tick(self._ups) / 1_000
        pg.display.set_caption(f"{self._caption} {1 / dt:.0f}FPS")

        self._last_frame_events = Events.read()

    def need_to_stop(self) -> bool:
        return pg.QUIT in self._last_frame_events

    def stop(self) -> None:
        pg.quit()
