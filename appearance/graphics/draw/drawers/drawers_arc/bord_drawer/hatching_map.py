from collections import defaultdict

from attrs import frozen, field

import appearance.protocols as proto
from color import Color
from mathematics.vector import Vector2Int
from statuses import Status, MISSING


@frozen
class HatchingMap(proto.HatchingMap):
    _color_at: dict[Vector2Int, Color] = field(init=False, factory=dict)
    _coords_with: dict[Color, set[Vector2Int]] = field(init=False, factory=lambda: defaultdict(set))

    def color_at(self, coord: Vector2Int) -> Color | Status:
        return self._color_at.get(coord, MISSING)

    def coords_with(self, color: Color) -> list[Vector2Int]:
        return self._coords_with.get(color, [])

    def set_color_at(self, coord: Vector2Int, color: Color) -> None:
        if coord in self._color_at:
            self._coords_with[self._color_at[coord]].remove(coord)

        self._color_at[coord] = color
        self._coords_with[color].add(coord)

    def remove_at(self, coord: Vector2Int) -> None:
        assert coord in self._color_at

        self._coords_with[self._color_at[coord]].remove(coord)
        self._color_at.pop(coord)
