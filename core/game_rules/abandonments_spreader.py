import math
import random
from typing import Iterator

from attrs import frozen

from my_random import temporarily_seed
from .game_rule import GameRule
import core.protocols as proto
import core.figures.figure as fig
from ..distant_neighbors_getter import DistantNeighborsGetter


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

    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        cells_cache = session.cells
        cells = cells_cache.with_owner(player)
        figures = session.figures

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
