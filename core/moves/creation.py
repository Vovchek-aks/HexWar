from attrs import frozen

import core.protocols as proto
from core.moves.valid_move import ValidMove
from core.protocols import Creatable
from mathematics.vector import Vector2Int
from statuses import Status, INVALID, MISSING


@frozen
class Creation(proto.Move):
    figure_type: type[proto.Figure]
    to_coord: Vector2Int

    def validate(self, session: proto.GameSession) -> proto.ValidMove | Status:
        board = session.board
        to_cell = board[self.to_coord]

        if to_cell.owner is not session.master.current_player:
            return INVALID

        if not to_cell.is_empty:
            return INVALID

        if to_cell.figure.is_on_land() != self.figure_type.is_on_land():
            return INVALID

        if (creatable := self.figure_type.FLAGS.get(Creatable)) is MISSING:
            return INVALID

        if not session.master.current_player.resources.can_take(creatable.cost):
            return INVALID

        return ValidMove(self)

    def execute(self, session: proto.GameSession) -> None:
        board = session.board

        session.figures.add(self.figure_type, self.to_coord)
        figure = board[self.to_coord].figure

        session.master.current_player.resources.take(figure.FLAGS.get(Creatable).cost)
