import random
from typing import Callable

from attrs import frozen

from core import protocols as proto
from core.cells import Cells
from core.figures import figure as fig
from mathematics.vector import Vector2Int
from my_types import ContextManager


@frozen
class ByGameRulesSessionChanger(proto.ByGameRulesSessionChanger):
    _session: proto.GameSession
    _multiple_cells_change: Callable[[Cells], ContextManager[None]]
    _on_changed_cell_owner: Callable[[Vector2Int], None]

    @property
    def _board(self) -> proto.Board:
        return self._session.board

    def on_turn_start(self) -> None:
        board = self._session.board
        player = self._session.master.current_player
        cells = self._session.cells.with_owner(player)

        to_update = cells.with_flag(proto.UpdatableOnTurnStart)
        priority_order = sorted(to_update, key=lambda cell: cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).priority)

        for cell in priority_order:
            cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).update(board.coordinates_of(cell), self._session)

    def on_turn_end(self) -> None:
        player = self._session.master.current_player
        cells = self._session.cells.with_owner(player)
        capitals = cells & self._session.cells.with_figure(fig.Capital)

        cells = self._discard_regions_without(capitals, cells)
        regions = self._get_regions_to_be_annexed(cells)
        for region in regions:
            self.annex(region)

    def annex(self, region: Cells) -> None:
        manned = region & self._session.cells.with_figure(fig.Infantry | fig.Motorization)
        for cell in manned:
            self._session.figures.remove(cell.figure)

        with self._multiple_cells_change(region):
            while region:
                annexed = self._annex_boundry(region)
                if not annexed:
                    break
                region -= annexed

        for cell in region:
            self._session.cells.update(cell)

    def _discard_regions_without(self, targets: Cells, cells: Cells) -> Cells:
        while targets:
            target = targets.any
            targets = targets.without(target)

            region = self._board.get_region_with_same_owner(target)
            cells -= region
            targets -= region

        return cells

    def _get_regions_to_be_annexed(self, cells: Cells) -> list[Cells]:
        regions_to_be_annexed = list[proto.Cells]()
        while cells:
            cell = cells.any
            cells = cells.without(cell)

            region = self._board.get_region_with_same_owner(cell)

            near_water = region.at_outer_boundry(self._board).with_flag(proto.AtWater)
            manned = region & self._session.cells.with_figure(fig.Infantry | fig.Motorization)
            if not (near_water and manned):
                regions_to_be_annexed.append(region)

            cells -= region

        return regions_to_be_annexed

    def _annex_boundry(self, region: Cells) -> Cells:
        to_annex = list[tuple[proto.Cell, proto.Player]]()
        boundry = region.at_inner_boundry(self._board)
        for cell in boundry:
            neighbors = (self._board.get_neighbors(cell) - region).with_flag(proto.OnLand)
            neighbors -= neighbors.with_owner(cell.owner)
            if not neighbors:
                continue

            annexer = random.choice(neighbors.as_list()).owner
            to_annex.append((cell, annexer))

        for cell, annexer in to_annex:
            cell.change_owner(annexer)
            self._on_changed_cell_owner(self._board.coordinates_of(cell))

        return Cells({pair[0] for pair in to_annex})
