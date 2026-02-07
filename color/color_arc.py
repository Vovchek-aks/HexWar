import math

import arcade as arc


class Color(arc.color.Color):
    @classmethod
    def average(cls, *colors: "Color") -> "Color":
        return cls.weighted_average(*((color, 1) for color in colors))

    @classmethod
    def weighted_average(cls, *pairs: tuple["Color", float]) -> "Color":
        total_r = total_g = total_b = 0
        total = 0
        for color, weight in pairs:
            total_r += color.r * weight
            total_g += color.g * weight
            total_b += color.b * weight
            total += weight
        return cls(math.floor(total_r / total),
                   math.floor(total_g / total),
                   math.floor(total_b / total))

    def lerp(self, color: "Color", ratio: float) -> "Color":
        return Color(
            min(255, round(self.r * (1 - ratio) + color.r * ratio)),
            min(255, round(self.g * (1 - ratio) + color.g * ratio)),
            min(255, round(self.b * (1 - ratio) + color.b * ratio))
        )
