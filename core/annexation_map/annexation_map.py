from collections import defaultdict
from typing import Iterator
from time import perf_counter as time

from attrs import frozen, field

import core.protocols as proto
from core.cells import Cells
from mathematics.hex_geometry import get_distance, DISTANCE_BETWEEN_CENTERS

TIME_TO_PROCESS_CELLS = 0.006


@frozen
class AnnexationMap(proto.AnnexationMap):
    _session: proto.GameSession

    _cells_to_annex_of: dict[proto.Player, set[proto.Cell]] = field(init=False, factory=lambda: defaultdict(set))

    def get_cells_to_annex_of(self, player: proto.Player) -> Cells:
        return Cells(self._cells_to_annex_of[player])

    def update_for(self, player: proto.Player) -> Iterator[None]:
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
            our_annexation_preventers = (region & with_flag).filter(lambda cell: cell.figure.FLAGS
                                                                    .get(proto.PreventsAnnexations)
                                                                    .can_prevent(board.coordinates_of(cell),
                                                                                 self._session, region))
            if not our_annexation_preventers:
                to_annex.update(region)
                continue

            enemy_annexation_preventers = Cells.empty()
            for enemy_annexation_preventers in self._get_enemy_annexation_preventers(board, region, with_flag):
                if enemy_annexation_preventers is None:
                    yield

            start = time()
            for cell in region & front:
                if time() - start >= TIME_TO_PROCESS_CELLS:
                    start = time()
                    yield
                if self._is_within_any_prevention_distance(cell, our_annexation_preventers):
                    continue
                if self._is_within_any_prevention_distance(cell, enemy_annexation_preventers):
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
            enemy_annexation_preventers += (with_flag & enemy_region).filter(lambda cell: cell.figure.FLAGS
                                                                             .get(proto.PreventsAnnexations)
                                                                             .can_prevent(board.coordinates_of(cell),
                                                                                          self._session, region))
        yield enemy_annexation_preventers

    def _is_within_any_prevention_distance(self, cell: proto.Cell, annexation_preventers: Cells) -> bool:
        board = self._session.board
        for annexation_preventer in annexation_preventers:
            distance = (annexation_preventer.figure.FLAGS.get(proto.PreventsAnnexations).distance *
                        DISTANCE_BETWEEN_CENTERS)
            if get_distance(board.coordinates_of(cell),
                            board.coordinates_of(annexation_preventer)) <= distance:
                return True
        return False

    def __contains__(self, cell: proto.Cell) -> bool:
        for cells in self._cells_to_annex_of.values():
            if cell in cells:
                return True
        return False
