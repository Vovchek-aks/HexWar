from attrs import frozen
import pygame as pg

from graphics import protocols as proto
from vector import Vector2Int


@frozen
class Camera(proto.Camera):
    _shape: Vector2Int
    _orientation: proto.CameraOrientation

    def world_to_screen(self, point: pg.Vector2) -> pg.Vector2:
        orient = self._orientation
        center = self._shape.as_float / 2 / orient.zoom
        position = orient.position + center
        return ((point - position).rotate(orient.rotation.degrees) + center) * orient.zoom
