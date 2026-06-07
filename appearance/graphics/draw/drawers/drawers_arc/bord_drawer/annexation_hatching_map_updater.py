from typing import Iterator

from attrs import define, field

import appearance.protocols as proto
from appearance.graphics.colors import WHITE
from core.cells import Cells
from core.protocols import GameSession, ByGameRulesSessionChanger, Player, MovesMaker
from statuses import Status, MISSING, ABORT_NEEDED

COLOR = WHITE


@define
class AnnexationHatchingMapUpdater:
    @classmethod
    def make(cls,
             hatching_map: proto.HatchingMap,
             board_drawer: proto.BordDrawer,
             moves_maker: MovesMaker,
             session_changer: ByGameRulesSessionChanger,
             session: GameSession) -> "AnnexationHatchingMapUpdater":
        self = cls(hatching_map, board_drawer, session_changer, session)
        moves_maker.board_move_was_made.subscribe(lambda _: self._on_board_move_was_made())
        session.master.turn_has_passed.subscribe(self._on_turn_has_passed)
        return self

    _hatching_map: proto.HatchingMap
    _board_drawer: proto.BordDrawer
    _session_changer: ByGameRulesSessionChanger
    _session: GameSession

    _process: Iterator[None | Cells] | Status = field(init=False, default=MISSING)

    @property
    def is_active(self) -> bool:
        return self._process is not MISSING

    def update(self) -> None:
        if not self.is_active:
            return

        result = next(self._process, ABORT_NEEDED)
        if result is ABORT_NEEDED:
            self._process = MISSING
            return

        if result is None:
            return

        self._process = self._update_hatching_map_process(*result)

    def start_process_for(self, player: Player, *, frames_to_skip: int = 0) -> None:
        self._process = self._get_cells_to_annex_process(player, frames_to_skip)

    def _on_board_move_was_made(self) -> None:
        self.start_process_for(self._session.master.current_player, frames_to_skip=30)

    def _on_turn_has_passed(self, player: Player) -> None:
        self.start_process_for(player)

    def _get_cells_to_annex_process(self,
                                    player: Player,
                                    frames_to_skip: int) -> Iterator[None | tuple[Cells, list[Player]]]:
        for _ in range(frames_to_skip):
            yield

        players = (self._session.cells.with_owner(player)
                   .at_outer_boundry(self._session.board)
                   .players())
        players.add(player)

        cells = Cells.empty()
        for player in players:
            result = Cells.empty()
            for result in self._session_changer.get_cells_to_annex_process(player):
                if result is None:
                    yield
            cells += result

        yield cells, players

    def _update_hatching_map_process(self, to_annex: Cells, players: list[Player]) -> Iterator[None]:
        board = self._session.board

        all_cells = Cells.empty()
        for player in players:
            yield
            all_cells += self._session.cells.with_owner(player)

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
