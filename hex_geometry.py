from math import cos, pi

from attrs import frozen
from pygame import Vector2

from ordered_dict import OrderedDict
from vector import Vector2Int


# https://vk.com/cyberdilf?w=wall-226630281_64


@frozen(eq=False, hash=True)
class Neighbor:
    def __eq__(self, other: 'Neighbor') -> bool:
        return self is other


NEIGHBORS = [
    TopCenter := Neighbor(),
    TopRight := Neighbor(),
    DownRight := Neighbor(),
    DownCenter := Neighbor(),
    DownLeft := Neighbor(),
    TopLeft := Neighbor()
]

OPPOSITE_NEIGHBOR = {
    TopCenter: DownCenter,
    TopRight: DownLeft,
    DownRight: TopLeft,
    DownCenter: TopCenter,
    DownLeft: TopRight,
    TopLeft: DownRight,
}


def neighbor_square_deltas() -> dict[Neighbor, Vector2Int]:
    return {
        TopCenter: Vector2Int(0, -1),
        TopRight: Vector2Int(1, 0),
        DownRight: Vector2Int(1, 1),
        DownCenter: Vector2Int(0, 1),
        DownLeft: Vector2Int(-1, 0),
        TopLeft: Vector2Int(-1, -1)
    }


def neighbors_vertexes() -> dict[Neighbor, tuple[Vector2, Vector2]]:
    _ver = Vector2(1, 0).rotate(120)
    return {
        TopCenter: (_ver, _ver := _ver.rotate(-60)),
        TopRight: (_ver, _ver := _ver.rotate(-60)),
        DownRight: (_ver, _ver := _ver.rotate(-60)),
        DownCenter: (_ver, _ver := _ver.rotate(-60)),
        DownLeft: (_ver, _ver := _ver.rotate(-60)),
        TopLeft: (_ver, _ver := _ver.rotate(-60)),
    }


DISTANCE_BETWEEN_CENTERS = (1.5 ** 2 + cos(pi / 6) ** 2) ** .5

X_NORM = (Vector2(1, 0) + Vector2(1, 0).rotate(60)).normalize() * DISTANCE_BETWEEN_CENTERS
Y_NORM = Vector2(0, -1) * DISTANCE_BETWEEN_CENTERS

if __name__ == '__main__':
    print(neighbor_square_deltas())
    print(neighbors_vertexes())
    print(f'{X_NORM=}')
    print(f'{Y_NORM=}')
