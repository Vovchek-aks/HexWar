import random
from typing import Callable

from attrs import frozen

from core import protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter
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

        for region in (self.get_cells_to_annex(player).split(self._session.board)):
            self.annex(region)

    def get_cells_to_annex(self, player: proto.Player) -> Cells:  # God abandoned this place
        cells = self._session.cells
        board = self._session.board
        player_cells = cells.with_owner(player)

        with_flag = (cells.not_empty().with_flag(proto.PreventsAnnexations)
                     .filter(lambda cell: cell.figure.FLAGS.get(proto.PreventsAnnexations)
                             .can_prevent(board.coordinates_of(cell), board)))
        not_to_annex = set[proto.Cell]()
        necessary_to_annex = list[Cells]()
        for region in player_cells.split(board):
            if not region & with_flag:
                necessary_to_annex.append(region)
                continue

            for cell in with_flag & region:
                distance = cell.figure.FLAGS.get(proto.PreventsAnnexations).distance

                not_to_annex |= (DistantNeighborsGetter(cell, board)
                                 .get_all_not_farther_than(distance, include_cell=True)
                                 & region).as_set()

        cannot_hold = player_cells - Cells(not_to_annex)

        to_annex = set[proto.Cell]()
        for region in cannot_hold.split(board):
            neighbors = Cells.combine(*(neighbor for neighbor in region.get_neighbor_regions(board)
                                        if neighbor.any.owner is not player))
            for cell in with_flag & neighbors:
                distance = cell.figure.FLAGS.get(proto.PreventsAnnexations).distance
                to_annex |= (DistantNeighborsGetter(cell, board)
                             .get_all_not_farther_than(distance, include_cell=True)
                             .as_set())

        return cannot_hold & Cells(to_annex) + Cells.combine(*necessary_to_annex)

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

    def _discard_regions_with(self, targets: Cells, cells: Cells) -> Cells:
        while targets:
            target = targets.any
            targets = targets.without(target)

            region = self._board.get_region_with_same_owner(target)
            cells -= region
            targets -= region

        return cells

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
            cell.change_owner_to(annexer)
            self._on_changed_cell_owner(self._board.coordinates_of(cell))

        return Cells({pair[0] for pair in to_annex})
