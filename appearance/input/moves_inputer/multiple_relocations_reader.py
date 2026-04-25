from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from core.cells import Cells
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import GameSession, Player, Movable
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

        selected = self._cell_selector.get_coord()
        if selected is MISSING:
            return False

        return Movable in self._session.board[selected].figure.FLAGS

    def get_path(self, from_coord: Vector2Int, to_coord: Vector2Int) -> list[Vector2Int]:
        assert (movable := self._session.board[from_coord].figure.FLAGS.get(Movable)) is not MISSING

        player = self._session.master.current_player
        board = self._session.board
        strength = movable.strength(from_coord, board)
        allowed = self._get_allowed(player, board[to_coord].owner, strength)
        path = PathSearcher(self._session.board, allowed, board[to_coord]).search_from(board[from_coord])
        return path

    def _get_allowed(self, from_player: Player, to_player: Player, strength: int) -> Cells:
        cells = self._session.cells
        allowed = (cells.with_owner(from_player) &
                   cells.with_figure(fig.Land))

        if to_player == from_player:
            return allowed

        allowed += Cells(set(filter(lambda cell: cell.hardness(self._session.board) <= strength,
                                    cells.with_owner(to_player))))
        return allowed
