from math import pi

from attrs import frozen, field
import pygame as pg


@frozen
class Angle:
    @classmethod
    def from_radians(cls, radians: float) -> "Angle":
        return cls(180 * radians / pi)

    degrees: float = field(converter=lambda deg: deg % 360)

    @property
    def radians(self) -> float:
        return pi * self.degrees / 180

    @property
    def inverse(self) -> "Angle":
        return self * -1

    def apply(self, vector: pg.Vector2) -> pg.Vector2:
        return vector.rotate(-self.degrees)

    def __add__(self, other: "Angle") -> "Angle":
        return type(self)(self.degrees + other.degrees)

    def __mul__(self, other: float) -> "Angle":
        return type(self)(self.degrees * other)

    def __neg__(self) -> "Angle":
        return self.inverse
