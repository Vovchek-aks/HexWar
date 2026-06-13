from typing import Iterator

from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.colors import WHITE
from core.cells import Cells
from core.protocols import GameSession, Player, AnnexationMapUpdater
from statuses import Status, MISSING, ABORT_NEEDED

COLOR = WHITE


@define
class AnnexationHatchingMapUpdater(proto.AnnexationHatchingMapUpdater):
    @classmethod
    def make(cls,
             session: GameSession,
             hatching_map: proto.HatchingMap,
             board_drawer: proto.BordDrawer,
             annexation_map_updater: AnnexationMapUpdater) -> "AnnexationHatchingMapUpdater":
        self = cls(session, hatching_map, board_drawer, annexation_map_updater)
        annexation_map_updater.update_for_player_was_finished.subscribe(
            lambda player: self._players_queue.append(player)
        )
        annexation_map_updater.update_for_player_was_requested.subscribe(self._on_update_for_player_was_requested)
        return self

    _session: GameSession
    _hatching_map: proto.HatchingMap
    _board_drawer: proto.BordDrawer
    _annexation_map_updater: AnnexationMapUpdater

    _players_queue: list[Player] = field(init=False, factory=list)
    _process: Iterator[None] | Status = field(init=False, default=MISSING)

    @property
    def is_active(self) -> bool:
        return self._process is not MISSING

    def update(self) -> None:
        if self.is_active:
            if next(self._process, ABORT_NEEDED) is not ABORT_NEEDED:
                return
            self._players_queue.pop(0)
            self._process = MISSING

        if not self._players_queue:
            return

        self._process = self._update_hatching_map_process(self._players_queue[0])

    def _on_update_for_player_was_requested(self, player: Player) -> None:
        if not self._players_queue:
            return

        if player is self._players_queue[0]:
            self._process = MISSING

        if player in self._players_queue:
            self._players_queue.remove(player)

    def _update_hatching_map_process(self, player: Player) -> Iterator[None]:
        board = self._session.board

        to_annex = self._annexation_map_updater.map.get_cells_to_annex_of(player)
        all_cells = self._session.cells.with_owner(player)
        colored = Cells(set(map(board.at, self._hatching_map.coords_with(COLOR)))) & all_cells

        to_color = to_annex - colored
        to_remove = colored - to_annex

        for cell in to_color:
            yield
            coord = board.coordinates_of(cell)
            self._hatching_map.set_color_at(coord, COLOR)
            self._board_drawer.update_hatching(coord)

        for cell in to_remove:
            yield
            coord = board.coordinates_of(cell)
            self._hatching_map.remove_at(coord)
            self._board_drawer.update_hatching(coord)
