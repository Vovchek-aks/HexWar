from attrs import define
from pygame import Vector2

from graphics import protocols as proto


@define
class Camera(proto.Camera):
    def transform(self, point: Vector2) -> Vector2:
        return Vector2(300, 400) + point * 50  # temp
