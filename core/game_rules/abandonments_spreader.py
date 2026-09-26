import math
import random
from typing import Iterator

from attrs import frozen, define, field

from mathematics.vector import Vector2Int
from my_random import temporarily_seed
from statuses import Status, MISSING
from .game_rule import GameRule
import core.protocols as proto
import core.figures.figure as fig
from ..distant_neighbors_getter import DistantNeighborsGetter


@define
class AbandonmentsSpreaderState(proto.GameRuleState):
    _was_any_abandonment_destroyed: bool = False
    _session: proto.GameSession | Status = field(init=False, default=MISSING)

    @property
    def was_any_abandonment_destroyed(self) -> bool:
        return self._was_any_abandonment_destroyed

    def set_session(self, session: proto.GameSession) -> None:
        assert self._session is MISSING
        self._session = session
        session.figures.figure_was_removed.subscribe(self._on_figure_was_removed)

    def on_turn_start(self) -> None:
        self._was_any_abandonment_destroyed = False

    def _on_figure_was_removed(self, figure: fig.Figure, coord: Vector2Int) -> None:
        assert self._session is not MISSING

        if self._was_any_abandonment_destroyed:
            return

        if not isinstance(figure, fig.Abandonment):
            return

        if self._session.board[coord].owner is not self._session.master.current_player:
            return

        self._was_any_abandonment_destroyed = True


@frozen
class AbandonmentsSpreader(GameRule):
    _PLATO = 3
    _SQUARE_GROWTH_LENGTH = 3
    _WAVE_AMPLITUDE = .5

    _TURN_RADIUS = 2
    _CAN_TURN = {
        fig.Town,
        fig.LightFactory,
        fig.HeavyFactory,
        fig.Settlement,
        fig.PrivateLightFactory,
        fig.PrivateHeavyFactory
    }

    @classmethod
    def get_to_spawn(cls, count: int, session: proto.GameSession) -> int:
        # https://www.desmos.com/calculator/kjz1ypimkn

        to_spawn = (cls._PLATO * (count / cls._SQUARE_GROWTH_LENGTH) ** 2
                    if count < cls._SQUARE_GROWTH_LENGTH else
                    cls._PLATO - cls._WAVE_AMPLITUDE * math.sin(count - cls._SQUARE_GROWTH_LENGTH))
        rounded = math.floor(to_spawn)
        with temporarily_seed(session.master.current_turn):
            return rounded + (1 if random.random() < to_spawn - rounded else 0)

    def on_turn_start(self, session: proto.GameSession) -> Iterator[None]:
        session.game_rule_states.get(AbandonmentsSpreaderState).on_turn_start()
        yield

    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        cells_cache = session.cells
        cells = cells_cache.with_owner(player)
        figures = session.figures
        state = session.game_rule_states.get(AbandonmentsSpreaderState)

        if state.was_any_abandonment_destroyed:
            return

        abandonments = cells & session.cells.with_figure(fig.Abandonment)
        if not abandonments:
            return

        to_spawn = self.get_to_spawn(len(abandonments), session)

        with temporarily_seed(session.master.current_turn):
            shuffled = abandonments.as_list()
            random.shuffle(shuffled)

        for abandonment in shuffled:
            yield
            if to_spawn <= 0:
                break

            neighbors = (DistantNeighborsGetter(abandonment, board)
                         .get_all_not_farther_than(self._TURN_RADIUS, include_cell=False))
            for neighbor in neighbors:
                if type(neighbor.figure) not in self._CAN_TURN:
                    continue

                figures.remove(neighbor.figure)
                figures.add(fig.Abandonment, board.coordinates_of(neighbor))
                to_spawn -= 1
                break
