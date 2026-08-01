from attrs import frozen

import core.protocols as proto
from core.cells import Cells


@frozen
class DistantNeighborsGetter:
    cell: proto.Cell
    board: proto.Board

    def get_all_not_farther_than(self, distance: int, *, include_cell: bool) -> proto.Cells:
        cells = Cells({self.cell})
        last_layer = cells
        for _ in range(distance):
            additional_cells = Cells.empty()
            for cell in last_layer:
                additional_cells += self.board.get_neighbors(cell, include_cell=False)
            additional_cells -= cells
            last_layer = additional_cells
            cells += additional_cells

        if not include_cell:
            cells -= Cells({self.cell})

        return cells

    def get_as_far_as(self, distance: int) -> proto.Cells:
        return self.get_all_not_farther_than(distance - 1, include_cell=True).at_outer_boundry(self.board)
