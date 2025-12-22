from math import pi

from attrs import frozen, field

from mathematics.vector import Vector2

ROTATION_DIRECTION = 1


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

    def apply(self, vector: Vector2) -> Vector2:
        return vector.rotate(self.degrees * ROTATION_DIRECTION)

    def __add__(self, other: "Angle") -> "Angle":
        return type(self)(self.degrees + other.degrees)

    def __mul__(self, other: float) -> "Angle":
        return type(self)(self.degrees * other)

    def __neg__(self) -> "Angle":
        return self.inverse
