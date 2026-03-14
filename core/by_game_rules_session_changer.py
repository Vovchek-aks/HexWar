import random
from typing import Callable

from attrs import frozen

from core import protocols as proto
from core.figures import figure as fig
from mathematics.vector import Vector2Int
from my_types import ContextManager


@frozen
class ByGameRulesSessionChanger(proto.ByGameRulesSessionChanger):
    _session: proto.GameSession
    _multiple_cells_change: Callable[[proto.Cells], ContextManager[None]]
    _on_changed_cell_owner: Callable[[Vector2Int], None]

    @property
    def board(self) -> proto.Board:
        return self._session.board

    def on_turn_start(self) -> None:
        player = self._session.master.current_player
        cells = (self._session.cells
                 .with_owner(player)
                 .with_flag(proto.UpdatableOnTurnStart))

        for cell in cells:
            coord = self.board.coordinates_of(cell)
            (cell.figure.FLAGS
             .get(proto.UpdatableOnTurnStart)
             .update(coord, self._session))

    def on_turn_end(self) -> None:
        player = self._session.master.current_player
        cells = self._session.cells.with_owner(player)
        capitals = cells & self._session.cells.with_figure(fig.Capital)

        cells = self._discard_regions_without(capitals, cells)
        regions = self._get_regions_to_be_annexed(cells)
        self._annex(regions)

    def _discard_regions_without(self, targets: proto.Cells, cells: proto.Cells) -> proto.Cells:
        while targets:
            target = targets.any
            targets = targets.without(target)

            region = self.board.get_region_with_same_owner(target)
            cells -= region
            targets -= region

        return cells

    def _get_regions_to_be_annexed(self, cells: proto.Cells) -> list[proto.Cells]:
        regions_to_be_annexed = list[proto.Cells]()
        while cells:
            cell = cells.any
            cells = cells.without(cell)

            region = self.board.get_region_with_same_owner(cell)

            boundry = region.at_outer_boundry(self.board)
            if not (boundry.with_flag(proto.AtWater) and region.with_figure(fig.Infantry | fig.Motorization)):
                regions_to_be_annexed.append(region)

            cells -= region

        return regions_to_be_annexed

    def _annex(self, regions: list[proto.Cells]) -> None:
        for region in regions:
            manned = region & self._session.cells.with_figure(fig.Infantry | fig.Motorization)
            for cell in manned:
                self._session.figures.remove(cell.figure)

            with self._multiple_cells_change(region):
                while region:
                    region -= self._annex_boundry(region)

    def _annex_boundry(self, region: proto.Cells) -> proto.Cells:
        to_annex = list[tuple[proto.Cell, proto.Player]]()
        boundry = region.at_inner_boundry(self.board)
        for cell in boundry:
            neighbors = (self.board.get_neighbors(cell) - region).with_flag(proto.OnLand)
            if not neighbors:
                continue

            annexer = random.choice(neighbors.as_list()).owner
            to_annex.append((cell, annexer))

        for cell, annexer in to_annex:
            cell.change_owner(annexer)
            self._on_changed_cell_owner(self.board.coordinates_of(cell))

        return boundry
