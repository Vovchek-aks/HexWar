from typing import Callable

from attrs import define
import arcade as arc

from appearance import protocols as proto
from appearance.graphics.colors import BACKGROUND
from .shape_list_drawer import ShapeListDrawer
from core.protocols import Board
from mathematics.vector import Vector2Int, Vector2
from mathematics.angle import Angle
from appearance.graphics.camera.camera_orientation import CameraOrientation


@define
class BordDrawer(proto.BordDrawer):
    @classmethod
    def make(cls,
             screen_shape: Vector2Int,
             camera: proto.Camera,
             board: Board) -> "BordDrawer":
        arcade_camera = arc.Camera2D()
        shape_list_drawer = ShapeListDrawer.make(board)
        self = cls(screen_shape, camera, camera.orientation.mutable_copy(), arcade_camera, shape_list_drawer)
        camera.orientation.has_changed.subscribe(self._update_arcade_camera_orientation)
        return self

    _screen_shape: Vector2Int
    _camera: proto.Camera
    _orientation: CameraOrientation
    _arcade_camera: arc.Camera2D
    _shape_list_drawer: ShapeListDrawer

    def draw_board(self) -> None:
        self._draw(self._shape_list_drawer.draw)

    def draw_highlighted(self, cell_coord: Vector2Int, highlight_ratio: float) -> None:
        self._draw(lambda: self._shape_list_drawer.draw_highlighted(cell_coord, highlight_ratio))

    def draw_background(self) -> None:
        rectangle = arc.rect.LBWH(*Vector2Int.zero().tuple, *self._screen_shape.tuple)
        arc.draw_rect_filled(rectangle, BACKGROUND)

    def update_cell_color(self, cell_coord: Vector2Int) -> None:
        self._shape_list_drawer.update_color(cell_coord)

    def _draw(self, draw: Callable[[], None]) -> None:
        camera = self._arcade_camera
        orientation = CameraOrientation(Vector2(*camera.position), Angle(camera.angle), camera.zoom)
        self._update_arcade_camera(self._orientation)
        self._arcade_camera.use()
        draw()
        self._update_arcade_camera(orientation)
        self._arcade_camera.use()

    def _update_arcade_camera_orientation(self) -> None:
        self._orientation = self._camera.orientation.mutable_copy()

    def _update_arcade_camera(self, orientation: CameraOrientation) -> None:
        position, rotation, zoom = orientation.tuple
        self._arcade_camera.position = position.tuple
        self._arcade_camera.angle = rotation.degrees
        self._arcade_camera.zoom = zoom
