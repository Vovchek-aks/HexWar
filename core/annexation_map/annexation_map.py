from collections import defaultdict
from typing import Iterator
from time import perf_counter as time

from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells
from core.distant_neighbors_getter import DistantNeighborsGetter

TIME_TO_PROCESS_CELLS = 0.006
SMALL_ENOUGH_DISTANCE = 3


@frozen
class AnnexationMap(proto.AnnexationMap):
    _session: proto.GameSession

    _cells_to_annex_of: dict[proto.Player, set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))

    def get_cells_to_annex_of(self, player: proto.Player) -> Cells:
        return Cells(self._cells_to_annex_of[player])

    def update_for(self, player: proto.Player, *, initial_frame_skips: int = 0) -> Iterator[None]:
        for _ in range(initial_frame_skips):
            yield

        cells = self._session.cells
        board = self._session.board
        player_cells = cells.with_owner(player)

        front = player_cells & cells.at_front
        yield

        with_flag = cells.not_empty().with_flag(proto.PreventsAnnexations)
        yield

        to_annex = set[proto.Cell]()
        for region in player_cells.split(board):
            yield
            our_annexation_preventers = (region & with_flag).filter(lambda cell:
                                                                    _flag_of(cell)
                                                                    .can_prevent(board.coordinates_of(cell),
                                                                                 self._session, region))
            if not our_annexation_preventers:
                to_annex.update(region)
                continue

            enemy_annexation_preventers = Cells.empty()
            for enemy_annexation_preventers in self._get_enemy_annexation_preventers(board, region, with_flag):
                if enemy_annexation_preventers is None:
                    yield

            groups = our_annexation_preventers.group_by(lambda cell: _flag_of(cell).distance > SMALL_ENOUGH_DISTANCE)
            nearby_our_annexation_preventers = groups.get(False, Cells.empty())
            faraway_our_annexation_preventers = groups.get(True, Cells.empty())
            yield

            groups = enemy_annexation_preventers.group_by(lambda cell: _flag_of(cell).distance > SMALL_ENOUGH_DISTANCE)
            nearby_enemy_annexation_preventers = groups.get(False, Cells.empty())
            faraway_enemy_annexation_preventers = groups.get(True, Cells.empty())
            yield

            start = time()
            for cell in region & front:
                if time() - start >= TIME_TO_PROCESS_CELLS:
                    yield
                    start = time()
                if self._is_within_any_prevention_distance(cell,
                                                           nearby_our_annexation_preventers,
                                                           faraway_our_annexation_preventers):
                    continue
                if self._is_within_any_prevention_distance(cell,
                                                           nearby_enemy_annexation_preventers,
                                                           faraway_enemy_annexation_preventers):
                    to_annex.add(cell)
                    continue

        self._cells_to_annex_of[player] = to_annex

    def _get_enemy_annexation_preventers(self,
                                         board: proto.Board,
                                         region: Cells,
                                         with_flag: Cells) -> Iterator[None | Cells]:
        enemy_annexation_preventers = Cells.empty()
        for enemy_region in region.get_neighbor_regions(board):
            yield
            enemy_annexation_preventers += (with_flag & enemy_region).filter(lambda cell:
                                                                             _flag_of(cell)
                                                                             .can_prevent(board.coordinates_of(cell),
                                                                                          self._session, region))
        yield enemy_annexation_preventers

    def _is_within_any_prevention_distance(self, cell: proto.Cell, nearby: Cells, faraway: Cells) -> bool:
        board = self._session.board

        surroundings = (DistantNeighborsGetter(cell, board)
                        .get_all_not_farther_than(SMALL_ENOUGH_DISTANCE, include_cell=False))
        if surroundings & nearby:
            return True

        for annexation_preventer in faraway:
            surroundings = self._session.cells.get_static_control_zone_of(annexation_preventer)
            if cell in surroundings:
                return True
        return False

    def __contains__(self, cell: proto.Cell) -> bool:
        for cells in self._cells_to_annex_of.values():
            if cell in cells:
                return True
        return False


def _flag_of(cell: proto.Cell) -> proto.PreventsAnnexations:
    return cell.figure.FLAGS.get(proto.PreventsAnnexations)
