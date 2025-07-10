from attrs import frozen
import pygame as pg

from appearance.graphics import protocols as proto
from mathematics.vector import Vector2Int


@frozen
class Camera(proto.Camera):
    _screen_shape: Vector2Int
    _orientation: proto.CameraOrientation

    def world_to_screen(self, point: pg.Vector2) -> pg.Vector2:
        center = self._screen_shape.as_float2 / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.apply(point - position) * zoom + center

    def screen_to_world(self, point: pg.Vector2) -> pg.Vector2:
        center = self._screen_shape.as_float2 / 2
        position, rotation, zoom = self._orientation.tuple
        return rotation.inverse.apply((point - center) / zoom) + position
