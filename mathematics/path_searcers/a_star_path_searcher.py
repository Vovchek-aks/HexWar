from typing import Iterator

from attrs import frozen

import core.protocols as proto
from core.cells import Cells
from core.protocols import Cell
from mathematics.hex_geometry import get_distance
from mathematics.path_searcers.path_searcher import PathSearcher, Path

Cost = float

@frozen
class AStarPathSearcher(PathSearcher):
    @classmethod
    def make(cls, board: proto.Board, target: Cell, *same_cost_cells: type[proto.Cells, Cost]) -> "AStarPathSearcher":
        return cls(board, cls.get_cost_of_from(*same_cost_cells), target)

    @classmethod
    def get_cost_of_from(cls, *same_cost_cells: type[proto.Cells, Cost]) -> dict[proto.Cell, Cost]:
        cost_of = dict[proto.Cell, Cost]()
        for cells, cost in same_cost_cells:
            for cell in cells:
                if cell not in cost_of:
                    cost_of[cell] = cost
        return cost_of

    _board: proto.Board
    _cost_of: dict[proto.Cell, Cost]
    _target: Cell

    def search_from(self, start_cell: Cell) -> Path:
        for path in self.search_process_from(start_cell):
            if path is not None:
                return path

    def search_process_from(self, start_cell: Cell) -> Iterator[Path | None]:
        if self._target not in self._cost_of:
            yield []

        neighbors = self._get_neighbors_of(start_cell)
        root_of = {neighbor: (start_cell, self._cost_of[neighbor]) for neighbor in neighbors}
        leafs = set(root_of)
        processed = {start_cell}

        yield from self._fill_process(root_of, leafs, processed)

        if self._target not in root_of:
            yield []

        path = Path()
        yield from self._fill_path_process(path, root_of, start_cell)
        yield path

    def _fill_process(self,
                      root_of: dict[Cell, tuple[Cell, Cost]],
                      leafs: set[Cell],
                      processed: set[Cell]) -> Iterator[None]:
        while leafs and self._target not in root_of:
            yield
            cell = self._pop_from(leafs, root_of)
            processed.add(cell)
            accumulated_cost = root_of[cell][1]
            neighbors = self._get_neighbors_of(cell) - Cells(processed)
            for neighbor in neighbors:
                neighbor_cost = accumulated_cost + self._cost_of[neighbor]
                if neighbor in root_of and root_of[neighbor][1] <= neighbor_cost:
                    continue

                root_of[neighbor] = cell, neighbor_cost
                leafs.add(neighbor)

    def _get_neighbors_of(self, target_cell: proto.Cell) -> proto.Cells:
        return self._board.get_neighbors(target_cell).filter(lambda cell: cell in self._cost_of)

    def _pop_from(self, leafs: set[Cell], root_of: dict[Cell, tuple[Cell, Cost]]) -> Cell:
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

    def _fill_path_process(self,
                           path: Path,
                           root_of: dict[Cell, tuple[Cell, Cost]],
                           start_cell: Cell) -> Iterator[None]:
        cell = self._target
        while cell != start_cell:
            yield
            path.append(self._board.coordinates_of(cell))
            cell = root_of[cell][0]
        path.append(self._board.coordinates_of(start_cell))
        path[:] = path[::-1]
