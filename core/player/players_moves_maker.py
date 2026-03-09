from typing import Iterator, Callable

from attrs import frozen

import core.protocols as proto
from my_types import ContextManager
from statuses import Status, MISSING
import core.figures.figure as fig

MovePreparationGetter = Callable[[proto.Move], Iterator[None] | Status]


def players_moves_maker(session: proto.GameSession,
                        moves_maker: proto.MovesMaker,
                        by_game_rules_session_changer: "ByGameRulesSessionChanger",
                        get_move_preparation_process: MovePreparationGetter = lambda _: MISSING) -> Iterator[None]:
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

        by_game_rules_session_changer.on_turn_end()
        session.master.pass_turn_to_next_player()
        session.figures_budget.clear()
        by_game_rules_session_changer.on_turn_start()


@frozen
class ByGameRulesSessionChanger:
    _session: proto.GameSession
    _multiple_cells_change: Callable[[proto.Cells], ContextManager[None]]

    def on_turn_start(self) -> None:
        player = self._session.master.current_player
        board = self._session.board
        cells = (self._session.cells
                 .with_owner(player)
                 .with_flag(proto.UpdatableOnTurnStart))

        for cell in cells:
            coord = board.coordinates_of(cell)
            (cell.figure.FLAGS
             .get(proto.UpdatableOnTurnStart)
             .update(coord, self._session))

    def on_turn_end(self) -> None:
        board = self._session.board
        player = self._session.master.current_player
        cells = self._session.cells.with_owner(player)
        capitals = cells & self._session.cells.with_figure(fig.Capital)

        while capitals:
            capital = capitals.any
            capitals = capitals.without(capital)

            region = board.get_region_with_same_owner(capital)
            cells -= region

            capitals -= region

        regions_to_be_annexed = list[tuple[proto.Cells, proto.Player]]()
        while cells:
            cell = cells.any
            cells = cells.without(cell)

            region = board.get_region_with_same_owner(cell)

            boundry = region.at_outer_boundry(board)
            if not boundry.with_flag(proto.AtWater):
                regions_to_be_annexed.append((region, boundry.any.owner))

            cells -= region

        for region, annexer in regions_to_be_annexed:
            manned = region & self._session.cells.with_figure(fig.Infantry | fig.Motorization)
            for cell in manned:
                self._session.figures.remove(cell.figure)

            with self._multiple_cells_change(region):
                for cell in region:
                    cell.change_owner(annexer)
