from typing import Iterator

import core.protocols as proto


def player_moves_maker(session: proto.GameSession,
                       moves_maker: proto.MovesMaker) -> Iterator[None]:
    while True:
        with session.master.current_player.inputer as player:
            player.move_was_inputted.subscribe(moves_maker.make)
            while not player.wants_to_end_turn():
                player.update(session)
                yield
            player.move_was_inputted.unsubscribe(moves_maker.make)

        session.master.pass_turn_to_next_player()
        session.figures_budget.clear()
