from attrs import frozen

from mathematics.vector import Vector2


@frozen
class Parabola:
    @classmethod
    def from_points(cls, point1: Vector2, point2: Vector2, point3: Vector2) -> "Parabola":
        x1, y1 = point1.tuple
        x2, y2 = point2.tuple
        x3, y3 = point3.tuple

        D = x1 * x1 * (x2 - x3) + x2 * x2 * (x3 - x1) + x3 * x3 * (x1 - x2)

        if abs(D) < 1e-12:
            a, b = 0, (y2 - y1) / (x2 - x1)
            return cls(a, b, y1 - b * x1)

        a = (y1 * (x2 - x3) + y2 * (x3 - x1) + y3 * (x1 - x2)) / D
        b = (x1 * x1 * (y2 - y3) + x2 * x2 * (y3 - y1) + x3 * x3 * (y1 - y2)) / D
        c = (x1 * x1 * (x2 * y3 - x3 * y2) + x2 * x2 * (x3 * y1 - x1 * y3) + x3 * x3 * (x1 * y2 - x2 * y1)) / D

        return cls(a, b, c)

    a: float
    b: float
    c: float

    def value(self, x: float) -> float:
        return self.a * x ** 2 + self.b * x + self.c
