from math import cos, pi

from attrs import frozen

from mathematics.matrix import Matrix2
from mathematics.vector import Vector2Int, Vector2


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


def _neighbor_square_deltas() -> dict[Neighbor, Vector2Int]:
    return {
        TopCenter: Vector2Int(0, -1),
        TopRight: Vector2Int(1, 0),
        DownRight: Vector2Int(1, 1),
        DownCenter: Vector2Int(0, 1),
        DownLeft: Vector2Int(-1, 0),
        TopLeft: Vector2Int(-1, -1)
    }


_NEIGHBOR_SQUARE_DELTAS = _neighbor_square_deltas()


def neighbor_square_deltas() -> dict[Neighbor, Vector2Int]:
    return _NEIGHBOR_SQUARE_DELTAS


def _neighbors_vertexes() -> dict[Neighbor, tuple[Vector2, Vector2]]:
    vertex = Vector2(1, 0).rotate(120)
    return {
        TopCenter: (vertex, vertex := vertex.rotate(-60)),
        TopRight: (vertex, vertex := vertex.rotate(-60)),
        DownRight: (vertex, vertex := vertex.rotate(-60)),
        DownCenter: (vertex, vertex := vertex.rotate(-60)),
        DownLeft: (vertex, vertex := vertex.rotate(-60)),
        TopLeft: (vertex, vertex.rotate(-60)),
    }


_NEIGHBOR_VERTEXES = _neighbors_vertexes()


def neighbors_vertexes() -> dict[Neighbor, tuple[Vector2, Vector2]]:
    return _NEIGHBOR_VERTEXES


DISTANCE_BETWEEN_CENTERS = (1.5 ** 2 + cos(pi / 6) ** 2) ** .5

X_NORM = (Vector2(1, 0) + Vector2(1, 0).rotate(60)).normalize() * DISTANCE_BETWEEN_CENTERS
Y_NORM = Vector2(0, -1) * DISTANCE_BETWEEN_CENTERS
_matrix = Matrix2.from_vectors(X_NORM, Y_NORM)


def get_world_position(cell_coord: Vector2Int) -> Vector2:
    return X_NORM * cell_coord.x + Y_NORM * cell_coord.y


def get_board_position(point: Vector2) -> Vector2Int:
    return Vector2Int.from_vector2(_matrix.inverse.apply(point), strict=False)


def get_direction(from_coord: Vector2Int, to_coord: Vector2Int) -> Vector2:
    return (get_world_position(to_coord) - get_world_position(from_coord)).normalize()


if __name__ == '__main__':
    print(neighbor_square_deltas())
    print(neighbors_vertexes())
    print(f'{X_NORM=}')
    print(f'{Y_NORM=}')
