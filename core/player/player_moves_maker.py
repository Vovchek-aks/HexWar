from typing import Iterator

import core.protocols as proto


def player_moves_maker(session: proto.GameSession,
                       moves_maker: proto.MovesMaker) -> Iterator[None]:
    while True:
        with session.master.current_player.inputer as player:
            _on_turn_start(session)
            while not player.wants_to_end_turn():
                move = player.get_move(session)
                if isinstance(move, proto.ValidMove):
                    moves_maker.make(move)
                yield

        session.master.pass_turn_to_next_player()
        session.figures_budget.clear()


def _on_turn_start(session: proto.GameSession) -> None:
    player = session.master.current_player
    board = session.board
    cells = (board.cells
             .with_owner(player)
             .with_flag(proto.UpdatableOnTurnStart))

    for cell in cells:
        coord = board.coordinates_of(cell)
        (cell.figure.FLAGS
         .get(proto.UpdatableOnTurnStart)
         .update(coord, session))
