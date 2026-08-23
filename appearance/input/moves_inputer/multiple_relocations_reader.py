from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from core.cells import Cells
from core.moves.relocations import Relocation, Assault
from core.moves.valid_move import ValidMove
from core.protocols import GameSession, Player, Movable, WithRestrictedTerrainKinds, CannotBeDestroyed, CanPull, \
    TerrainKind
from mathematics.path_searcers.a_star_path_searcher import AStarPathSearcher as PathSearcher
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
        board = self._session.board
        cells = self._session.cells
        cell = board[from_coord]
        target = board[to_coord]

        assert (movable := cell.figure.FLAGS.get(Movable)) is not MISSING

        player = self._session.master.current_player
        strength = movable.strength(from_coord, board)
        allowed = self._get_allowed(player, target.owner, strength, cell.figure)
        bad_terrains = cells.at_terrain(*self._get_bad_terrain_kinds_of(cell.figure))

        empties = allowed & cells.with_figure(fig.Land)
        movables = allowed.with_flag(Movable) - cells.at_changeable_front - board.get_neighbors(cell)

        good_and_empty = empties - bad_terrains
        good_with_movables = movables - bad_terrains
        bad_and_empty = empties & bad_terrains
        bad_with_movables = movables & bad_terrains

        possible_moves_count = (cell.figure.MOVES_BUDGET //
                                cell.figure.get_cost_of(Relocation(Vector2Int.zero(), Vector2Int.zero())))
        path_searcher = PathSearcher.make(board, target,
                                          (Cells({cell, target}), 0),
                                          (good_and_empty, 1),
                                          (bad_and_empty, possible_moves_count),
                                          (good_with_movables, 100),
                                          (bad_with_movables, 100 * possible_moves_count)
                                          )
        path = path_searcher.search_from(cell)
        return path

    def _get_allowed(self, from_player: Player, to_player: Player, strength: int, figure: fig.Figure) -> Cells:
        cells = self._session.cells
        allowed = (cells.with_owner(from_player) &
                   cells.with_figure(fig.Land))

        if to_player == from_player:
            return allowed

        allowed += (cells.with_owner(to_player)
                    .filter(lambda cell: cell.hardness(self._session.board) <= strength)
                    .filter(lambda cell: CannotBeDestroyed not in cell.figure.FLAGS)
                    - cells.at_terrain(*self._get_bad_terrain_kinds_of(figure)))

        return allowed

    def _get_bad_terrain_kinds_of(self, figure: fig.Figure | type[fig.Figure]) -> set[type[TerrainKind]]:
        result = (figure.FLAGS
                  .get(WithRestrictedTerrainKinds)
                  .terrain_kinds)

        if CanPull in figure.FLAGS and self._session.pulling_connections.is_puller(figure):
            result -= self._get_bad_terrain_kinds_of(self._session.pulling_connections.get_pullable(figure))

        return result
