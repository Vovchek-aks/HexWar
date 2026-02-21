from attrs import frozen

import core.protocols as proto
from mathematics.hex_geometry import get_distance
from mathematics.vector import Vector2Int

Path = list[Vector2Int]


@frozen
class GreedyPathSearcher:
    _board: proto.Board
    _allowed: proto.Cells
    _target: proto.Cell

    def search_from(self, cell: proto.Cell) -> Path:
        if self._target not in self._allowed:
            return []

        path = self._search_from(cell, path=[], seen=set())

        index = 0
        while index < len(path) - 1:
            coord = path[index]
            neighbors = self._board.get_neighbors(self._board[coord])
            for neighbor in neighbors:
                neighbor_coord = self._board.coordinates_of(neighbor)
                if neighbor_coord in path[index + 1:] and (neighbor_index := path.index(neighbor_coord)) > index + 1:
                    path = path[:index + 1] + path[neighbor_index:]
                    break

            index += 1

        return path

    def _search_from(self, cell: proto.Cell, *, path: Path, seen: set[proto.Cell]) -> Path:
        if cell in seen:
            return []
        seen.add(cell)

        neighbors = self._board.get_neighbors(cell) & self._allowed
        if not neighbors:
            return []

        path = path.copy()
        path.append(self._board.coordinates_of(cell))

        if cell is self._target:
            return path

        for next_cell in sorted(neighbors.all(), key=self._distance_to_target):
            try:
                full_path = self._search_from(next_cell, path=path, seen=seen)
            except RecursionError:
                return []
            if full_path:
                return full_path
        return []

    def _distance_to_target(self, cell: proto.Cell) -> float:
        return get_distance(self._board.coordinates_of(self._target),
                            self._board.coordinates_of(cell))
