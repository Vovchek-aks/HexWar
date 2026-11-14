from typing import Iterator

from attrs import frozen, Factory

import core.protocols as proto
from core.cells import Cells
from core.protocols import Cell
from mathematics.hex_geometry import get_distance
from mathematics.path_searcers.path_searcher import PathSearcher, Path

Cost = float


@frozen
class Node:
    cost: Cost
    parent: Cell
    children: set[Cell] = Factory(set)


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
        node_of = {neighbor: Node(self._cost_of[neighbor], start_cell) for neighbor in neighbors}
        leafs = set(node_of)

        yield from self._fill_process(node_of, leafs)

        if self._target not in node_of:
            yield []

        path = Path()
        yield from self._fill_path_process(path, node_of, start_cell)
        yield path

    def _fill_process(self,
                      node_of: dict[Cell, Node],
                      leafs: set[Cell]) -> Iterator[None]:
        while leafs and self._target not in node_of:
            yield
            cell = self._pop_from(leafs, node_of)
            accumulated_cost = node_of[cell].cost
            neighbors = self._get_neighbors_of(cell) - (Cells.from_iter(node_of) - Cells(leafs))
            for neighbor in neighbors:
                neighbor_cost = accumulated_cost + self._cost_of[neighbor]
                if neighbor in node_of and node_of[neighbor].cost <= neighbor_cost:
                    continue

                if neighbor in node_of:
                    self._remove_offsprings_of(neighbor, node_of, leafs)

                node_of[neighbor] = Node(neighbor_cost, cell)
                leafs.add(neighbor)
                node_of[cell].children.add(neighbor)

    def _remove_offsprings_of(self,
                              cell: Cell,
                              node_of: dict[Cell, Node],
                              leafs: set[Cell],
                              *,
                              _is_inner: bool = False) -> None:
        if not _is_inner:
            assert cell in node_of
            node_of[node_of[cell].parent].children.remove(cell)

        for child in node_of[cell].children:
            self._remove_offsprings_of(child, node_of, leafs, _is_inner=True)

        node_of.pop(cell)
        leafs.discard(cell)

    def _get_neighbors_of(self, target_cell: proto.Cell) -> proto.Cells:
        return self._board.get_neighbors(target_cell).filter(lambda cell: cell in self._cost_of)

    def _pop_from(self, leafs: set[Cell], node_of: dict[Cell, Node]) -> Cell:
        def key(cell: Cell) -> float:
            return (node_of[cell].cost +
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
                           node_of: dict[Cell, Node],
                           start_cell: Cell) -> Iterator[None]:
        cell = self._target
        while cell != start_cell:
            yield
            path.append(self._board.coordinates_of(cell))
            cell = node_of[cell].parent
        path.append(self._board.coordinates_of(start_cell))
        path[:] = path[::-1]
