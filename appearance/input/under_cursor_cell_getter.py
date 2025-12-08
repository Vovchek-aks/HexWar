from attrs import frozen

import appearance.protocols as proto
from core.protocols import Board
from mathematics.hex_geometry import get_board_position, get_world_position
from mathematics.vector import Vector2Int, Vector2
from statuses import Status, MISSING


@frozen
class UnderCursorCellGetter(proto.UnderCursorCellGetter):
    _camera: proto.Camera
    _board: Board

    def get_coord(self, screen_position: Vector2) -> Vector2Int | Status:
        board = self._board
        point = self._camera.screen_to_world(screen_position)

        rough_coord = get_board_position(point)
        if rough_coord not in board:
            return MISSING

        coord = self._refinish(rough_coord, point)
        if coord not in board:
            return MISSING

        return coord

    def _refinish(self, coord: Vector2Int, point: Vector2) -> Vector2Int:
        board = self._board
        true_cell = min(board.get_neighbors(board[coord], include_cell=True).all(),
                        key=lambda cell: (get_world_position(board.coordinates_of(cell)) - point).length())
        return board.coordinates_of(true_cell)
