from attrs import frozen, field
import arcade as arc

import appearance.protocols as proto
from appearance.input.clicks_catcher.click import MouseButtons
from appearance.input.moves_inputer.input_actions import CellClickAction
from core.moves.relocations import Relocation
from core.moves.valid_move import ValidMove
from core.protocols import GameSession
from mathematics.greedy_path_searcher import GreedyPathSearcher
from mathematics.vector import Vector2Int
from observer import Event, OnEventSubscriber
import core.figures.figure as fig
from statuses import MISSING

MULTIPLE_RELOCATIONS_KEY = arc.key.LSHIFT


@frozen
class MultipleRelocationsReader(proto.MultipleRelocationsReader):
    _session: GameSession
    _cell_selector: proto.CellSelector
    _input_state: proto.InputState

    def process(self, last_action: proto.InputAction) -> list[ValidMove]:
        match last_action:
            case CellClickAction(coord=click_coord, buttons=proto.MouseButtons(is_right=True)):
                ...
            case _:
                return []

        if MULTIPLE_RELOCATIONS_KEY not in self._input_state.pressed_keys:
            return []

        if (selected_coord := self._cell_selector.get_coord()) is MISSING:
            return []

        cells = self._session.cells
        player = self._session.master.current_player
        board = self._session.board
        allowed = cells.with_owner(player) & cells.with_figure(fig.Land)
        path = GreedyPathSearcher(self._session.board, allowed, board[click_coord]).search_from(board[selected_coord])
        if not path:
            return []

        moves = list[ValidMove]()
        for from_coord, to_coord in zip(path[:-1], path[1:]):
            moves.append(ValidMove(Relocation(from_coord, to_coord)))

        return moves
