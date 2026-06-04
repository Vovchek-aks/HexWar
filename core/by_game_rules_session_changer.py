import random
from typing import Callable, Iterator

from attrs import frozen

from core import protocols as proto
from core.cells import Cells
from core.figures import figure as fig
from mathematics.hex_geometry import get_distance
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

    def on_turn_end(self) -> Iterator[None]:
        player = self._session.master.current_player

        to_annex = Cells.empty()
        for to_annex in self.get_cells_to_annex_process(player):
            if to_annex is None:
                yield

        for region in (to_annex.split(self._session.board)):
            yield
            self.annex(region)

    def get_cells_to_annex(self, player: proto.Player) -> Cells:
        for cells in self.get_cells_to_annex_process(player):
            if cells is not None:
                return cells
        assert False

    def get_cells_to_annex_process(self, player: proto.Player) -> Iterator[None | Cells]:  # God abandoned this place
        cells = self._session.cells
        board = self._session.board
        player_cells = cells.with_owner(player)

        front = player_cells & cells.at_front

        with_flag = (cells.not_empty().with_flag(proto.PreventsAnnexations)
                     .filter(lambda cell: cell.figure.FLAGS.get(proto.PreventsAnnexations)
                             .can_prevent(board.coordinates_of(cell), board)))
        to_annex = set[proto.Cell]()
        for region in player_cells.split(board):
            yield
            if not region & with_flag:
                to_annex.update(region)
                continue

            our_annexation_preventers = with_flag & region
            enemy_annexation_preventers = with_flag & Cells.combine(*region.get_neighbor_regions(board))
            for cell in region & front:
                yield
                if self._is_within_any_prevention_distance(cell, our_annexation_preventers):
                    continue
                if self._is_within_any_prevention_distance(cell, enemy_annexation_preventers):
                    to_annex.add(cell)
                    continue

        yield Cells(to_annex)

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

    def _is_within_any_prevention_distance(self, cell: proto.Cell, annexation_preventers: Cells) -> bool:
        board = self._session.board
        for annexation_preventer in annexation_preventers:
            print(annexation_preventer.figure, annexation_preventer.figure.FLAGS)
            distance = annexation_preventer.figure.FLAGS.get(proto.PreventsAnnexations).distance
            if get_distance(board.coordinates_of(cell),
                            board.coordinates_of(annexation_preventer)) <= distance:
                return True
        return False

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
