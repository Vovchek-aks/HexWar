from typing import Iterator

from attrs import frozen

from .game_rule import GameRule
import core.protocols as proto


@frozen
class FiguresUpdateFlagCaller(GameRule):
    def on_turn_start(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        cells_cache = session.cells
        cells = cells_cache.with_owner(player)

        to_update = cells & cells_cache.with_flag(proto.UpdatableOnTurnStart)
        priority_order = sorted(to_update, key=lambda cell: cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).priority)

        for cell in priority_order:
            cell.figure.FLAGS.get(proto.UpdatableOnTurnStart).update(board.coordinates_of(cell), session)
        yield
