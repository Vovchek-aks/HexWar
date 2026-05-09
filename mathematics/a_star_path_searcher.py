from typing import Iterator

from attrs import frozen

import core.protocols as proto
from core.cells import Cells
from core.protocols import Cell
from mathematics.hex_geometry import get_distance
from mathematics.vector import Vector2Int

Path = list[Vector2Int]


@frozen
class AStarPathSearcher:
    _board: proto.Board
    _allowed: proto.Cells
    _target: Cell

    def search_from(self, start_cell: Cell) -> Path:
        for path in self.search_process_from(start_cell):
            if path is not None:
                return path

    def search_process_from(self, start_cell: Cell) -> Iterator[None | Path]:
        allowed = self._allowed
        if self._target not in allowed:
            yield []

        neighbors = self._board.get_neighbors(start_cell) & allowed
        root_of = {neighbor: (start_cell, 1) for neighbor in neighbors}
        leafs = set(root_of)
        processed = {start_cell}

        yield from self._fill_process(root_of, leafs, processed, allowed)

        if self._target not in root_of:
            yield []

        path = Path()
        yield from self._fill_path_process(path, root_of, start_cell)
        yield path

    def _fill_process(self,
                      root_of: dict[Cell, tuple[Cell, int]],
                      leafs: set[Cell],
                      processed: set[Cell],
                      allowed: Cells) -> Iterator[None]:
        while leafs and self._target not in root_of:
            yield
            cell = self._pop_from(leafs, root_of)
            processed.add(cell)
            distance_to_start = root_of[cell][1]
            neighbors = self._board.get_neighbors(cell) & allowed - Cells(processed)
            for neighbor in neighbors:
                if neighbor in root_of and root_of[neighbor][1] <= distance_to_start + 1:
                    continue

                root_of[neighbor] = cell, distance_to_start + 1
                leafs.add(neighbor)

    def _pop_from(self, leafs: set[Cell], root_of: dict[Cell, tuple[Cell, int]]) -> Cell:
        def key(cell: Cell) -> float:
            return (root_of[cell][1] +
                    self._distance_to_target(cell))

        leaf = min(leafs, key=key)
        leafs.remove(leaf)
        return leaf

    def _distance_to_target(self, cell: Cell) -> float:
        coord = self._board.coordinates_of(cell)
        target_coord = self._board.coordinates_of(self._target)
        return get_distance(target_coord, coord)

    def _fill_path_process(self, path: Path, root_of: dict[Cell, tuple[Cell, int]], start_cell: Cell) -> Iterator[None]:
        cell = self._target
        while cell != start_cell:
            yield
            path.append(self._board.coordinates_of(cell))
            cell = root_of[cell][0]
        path.append(self._board.coordinates_of(start_cell))
        path[:] = path[::-1]
