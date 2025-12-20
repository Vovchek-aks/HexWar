import arcade as arc


class Color(arc.color.Color):
    def lerp(self, color: "Color", ratio: float):
        return Color(
            min(255, round(self.r * (1 - ratio) + color.r * ratio)),
            min(255, round(self.g * (1 - ratio) + color.g * ratio)),
            min(255, round(self.b * (1 - ratio) + color.b * ratio))
        )
