import math

from attrs import frozen
import arcade as arc
import random

from appearance.graphics.colors import HIGHLIGHTED_WATER
from color import Color
from mathematics.vector import Vector2Int
from my_random import temporarily_seed

# https://www.desmos.com/calculator/ks2vewqatg

PERIOD_1_RANGE = 2.5, 5
PERIOD_2_RANGE = 10, 60
AMPLITUDE_RANGE = .5, 1


@frozen
class WaterAnimator:
    @classmethod
    def make(cls, sprites: dict[Vector2Int, arc.Sprite]) -> "WaterAnimator":
        base_color_at = dict[Vector2Int, Color]()
        periods_at = dict[Vector2Int, tuple[float, float]]()
        amplitude_at = dict[Vector2Int, float]()
        phase_at = dict[Vector2Int, float]()
        for coord, sprite in sprites.items():
            base_color_at[coord] = sprite.color
            with temporarily_seed(str(coord)):
                amplitude_at[coord] = random.uniform(*AMPLITUDE_RANGE)
                period_1 = random.uniform(*PERIOD_1_RANGE)
                period_2 = random.uniform(*PERIOD_2_RANGE)
                periods_at[coord] = period_1, period_2
                phase_at[coord] = random.uniform(0, 1)

        return cls(sprites, base_color_at, periods_at, amplitude_at, phase_at)

    _sprite_at: dict[Vector2Int, arc.Sprite]
    _base_color_at: dict[Vector2Int, Color]
    _periods_at: dict[Vector2Int, tuple[float, float]]
    _amplitude_at: dict[Vector2Int, float]
    _phase_at: dict[Vector2Int, float]

    def update_all(self, time: float) -> None:
        for coord in self._sprite_at:
            self.update_cell_at(coord, time)

    def update_cell_at(self, coord: Vector2Int, time: float) -> None:
        sprite = self._sprite_at[coord]
        ratio = self._get_lerp_ratio(coord, time)
        sprite.color = Color.lerp(self._base_color_at[coord], HIGHLIGHTED_WATER, ratio)

    def _get_lerp_ratio(self, coord: Vector2Int, time: float) -> float:
        amplitude = self._amplitude_at[coord]
        period_1, period_2 = self._periods_at[coord]
        phase = self._phase_at[coord]

        f1 = math.tau / period_1
        f2 = math.tau / period_2
        p = math.tau * phase - math.pi / 2
        a = amplitude / 4

        s = math.sin(f2 * time + p) + 1
        return a * s * math.sin(f1 * time) + 2 * a
