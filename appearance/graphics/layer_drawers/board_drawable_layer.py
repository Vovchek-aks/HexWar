from attrs import frozen

import appearance.protocols as proto
from appearance.input.moves_inputer.input_actions import OreshnikLaunchButtonPressAction, AttackButtonPressAction
from core.distant_neighbors_getter import DistantNeighborsGetter
from core.moves.oreshnik_launch import OreshnikLaunch
from core.protocols import GameSession, CanPull, Pullable, CanAttack
from mathematics.vector import Vector2, Vector2Int
from statuses import MISSING, Status


@frozen
class BoardDrawableLayer(proto.DrawableLayer):
    _session: GameSession
    _draw: proto.Draw
    _hovered_cell_getter: proto.UnderCursorCellGetter
    _cell_selector: proto.CellSelector
    _camera_assistant: proto.CameraAssistant
    _multiple_relocations_reader: proto.MultipleRelocationsReader
    _actions_reader: proto.InputActionsReader

    def draw(self, mouse_position: Vector2) -> None:
        with self._camera_assistant:
            self._draw_layer(mouse_position)

    def _draw_layer(self, mouse_position: Vector2) -> None:
        self._draw.board()
        hovered_coord = self._hovered_cell_getter.get_coord(mouse_position)
        selected_coord = self._cell_selector.get_coord()

        if hovered_coord is not MISSING:
            self._draw_path_if_needed(hovered_coord, selected_coord)
            self._draw_oreshnik_targets_if_needed(hovered_coord, selected_coord)
            self._draw_attack_targets_if_needed(hovered_coord, selected_coord)
            self._draw.under_cursor_cell(hovered_coord)

        if selected_coord is not MISSING:
            self._draw.selected_cell(selected_coord)
            self._draw_connected_if_needed(selected_coord)

        self._draw.board_sprites()

    def _draw_path_if_needed(self, hovered_coord: Vector2Int, selected_coord: Vector2Int | Status) -> None:
        if not self._multiple_relocations_reader.is_requested():
            return

        for coord in self._multiple_relocations_reader.get_path(selected_coord, hovered_coord):
            self._draw.interest_cell(coord)

    def _draw_oreshnik_targets_if_needed(self, hovered_coord: Vector2Int, selected_coord: Vector2Int | Status) -> None:
        if not self._is_highlighting_for_click_after_button_press_needed(hovered_coord, selected_coord,
                                                                         OreshnikLaunchButtonPressAction):
            return

        board = self._session.board
        for cell in OreshnikLaunch(selected_coord, hovered_coord).get_target_cells(self._session):
            self._draw.interest_cell(board.coordinates_of(cell))

    def _draw_attack_targets_if_needed(self, hovered_coord: Vector2Int, selected_coord: Vector2Int | Status) -> None:
        if not self._is_highlighting_for_click_after_button_press_needed(hovered_coord, selected_coord,
                                                                         AttackButtonPressAction):
            return

        board = self._session.board
        from_cell = board[selected_coord]
        distance = from_cell.figure.FLAGS.get(CanAttack).max_distance
        cells = DistantNeighborsGetter(from_cell, board).get_all_not_farther_than(distance, include_cell=False)
        for cell in cells:
            if not cell.figure.is_on_land():
                continue
            self._draw.interest_cell(board.coordinates_of(cell))

    def _is_highlighting_for_click_after_button_press_needed(self,
                                                             hovered_coord: Vector2Int,
                                                             selected_coord: Vector2Int | Status,
                                                             action: type[proto.InputAction]) -> bool:
        if selected_coord is MISSING:
            return False

        board = self._session.board
        if not board[hovered_coord].figure.is_on_land():
            return False

        last_action = self._actions_reader.last_action
        if last_action is MISSING:
            return False

        return isinstance(last_action, action)

    def _draw_connected_if_needed(self, selected_coord: Vector2Int) -> None:
        figure = self._session.board[selected_coord].figure
        if not (CanPull in figure.FLAGS or
                Pullable in figure.FLAGS):
            return

        connections = self._session.pulling_connections
        other = connections.get_connected(figure)
        if other is MISSING:
            return

        self._draw.interest_cell(self._session.figures.locate(other))
