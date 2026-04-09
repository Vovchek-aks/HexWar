from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import GameSession
from mathematics.a_star_path_searcher import AStarPathSearcher as PathSearcher
import core.figures.figure as fig
from mathematics.vector import Vector2Int
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

        if not self.is_requested():
            return []

        path = self.get_path(self._cell_selector.get_coord(), click_coord)
        if not path:
            return []

        player = self._session.master.current_player
        board = self._session.board
        moves = list[ValidMove]()
        for from_coord, to_coord in zip(path[:-1], path[1:]):
            move_type = Relocation if board[to_coord].owner is player else Assault
            moves.append(ValidMove(move_type.make(from_coord, to_coord)))

        return moves

    def is_requested(self) -> bool:
        if MULTIPLE_RELOCATIONS_KEY not in self._input_state.pressed_keys:
            return False

        return self._cell_selector.get_coord() is not MISSING

    def get_path(self, from_coord: Vector2Int, to_coord: Vector2Int) -> list[Vector2Int]:
        player = self._session.master.current_player
        board = self._session.board
        cells = self._session.cells
        allowed = ((cells.with_owner(player) +
                    cells.with_owner(board[to_coord].owner)) &
                   cells.with_figure(fig.Land))
        path = PathSearcher(self._session.board, allowed, board[to_coord]).search_from(board[from_coord])
        return path
