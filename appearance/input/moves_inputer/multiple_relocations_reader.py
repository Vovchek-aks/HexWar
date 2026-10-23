from attrs import frozen
import arcade as arc

import appearance.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from core.cells import Cells
from core.moves.relocations import Relocation, Assault, FiguresRelocation
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

        return self.get_moves_for(path)

    def get_moves_for(self, path: list[Vector2Int]) -> list[ValidMove[FiguresRelocation]]:
        if len(path) < 2:
            return []

        board = self._session.board
        player = board[path[0]].owner
        figure = board[path[0]].figure
        budget = figure.MOVES_BUDGET - self._session.figures_budget.of(figure)

        moves = list[ValidMove[FiguresRelocation]]()
        for from_coord, to_coord in zip(path[:-1], path[1:]):
            move_type = Relocation if board[to_coord].owner is player else Assault
            move = move_type.make(from_coord, to_coord)

            if (cost := figure.get_cost_of(move)) > budget:
                break

            moves.append(ValidMove(move))
            budget -= (budget
                       if figure.FLAGS.get(WithRestrictedTerrainKinds).contains_in(board[to_coord], board=board) else
                       cost)

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

        good = allowed - bad_terrains
        bad = allowed - good

        possible_moves_count = (cell.figure.MOVES_BUDGET //
                                cell.figure.get_cost_of(Relocation(Vector2Int.zero(), Vector2Int.zero())))
        path_searcher = PathSearcher.make(board, target,
                                          (Cells({cell, target}), 0),
                                          (good, 1),
                                          (bad, possible_moves_count))
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
        result = set(figure.FLAGS
                     .get(WithRestrictedTerrainKinds)
                     .terrain_kinds)

        if CanPull in figure.FLAGS and self._session.pulling_connections.is_puller(figure):
            result -= self._get_bad_terrain_kinds_of(self._session.pulling_connections.get_pullable(figure))

        return result
