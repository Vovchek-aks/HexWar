from abc import ABC, abstractmethod, ABCMeta

from pygame import Vector2


class Camera(ABC):
    @abstractmethod
    def transform(self, point: Vector2) -> Vector2:
        ...
