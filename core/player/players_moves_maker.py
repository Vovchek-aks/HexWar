from typing import Iterator, Callable

import core.protocols as proto
from statuses import Status, MISSING

MovePreparationGetter = Callable[[proto.Move], Iterator[None] | Status]
TurnStartPreparationGetter = Callable[[proto.Player], Iterator[None] | Status]
TurnEndPreparationGetter = Callable[[proto.Player], Iterator[None] | Status]


def players_moves_maker(session: proto.GameSession,
                        moves_maker: proto.MovesMaker,
                        by_game_rules_session_changer: proto.ByGameRulesSessionChanger,
                        get_move_preparation_process: MovePreparationGetter = lambda _: MISSING,
                        get_turn_start_preparation_process: TurnStartPreparationGetter = lambda _: MISSING,
                        get_turn_end_preparation_process: TurnEndPreparationGetter = lambda _: MISSING
                        ) -> Iterator[None]:
    process = get_turn_start_preparation_process(session.master.current_player)
    if process is not MISSING:
        yield from process

    while True:
        with session.master.current_player.inputer as player:
            while not player.wants_to_end_turn():
                yield
                move = player.get_move(session)
                if not isinstance(move, proto.ValidMove):
                    continue

                process = get_move_preparation_process(move.move)
                if process is not MISSING:
                    yield from process

                moves_maker.make(move)

        process = get_turn_end_preparation_process(session.master.current_player)
        if process is not MISSING:
            yield from process

        yield from by_game_rules_session_changer.on_turn_end()
        session.figures_budget.clear()

        process = get_turn_start_preparation_process(session.master.next_player)
        if process is not MISSING:
            yield from process

        session.master.pass_turn_to_next_player(session)
        by_game_rules_session_changer.on_turn_start()


