from math import pi

from attrs import frozen, field


@frozen
class Angle:
    @classmethod
    def from_radians(cls, radians: float) -> "Angle":
        return cls(180 * radians / pi)

    degrees: float = field(converter=lambda deg: deg % 360)

    @property
    def radians(self) -> float:
        return pi * self.degrees / 180

    def __add__(self, other: "Angle") -> "Angle":
        return type(self)(self.degrees + other.degrees)

    def __mul__(self, other: float) -> "Angle":
        return type(self)(self.degrees * other)
