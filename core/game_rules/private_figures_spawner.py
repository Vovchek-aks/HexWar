import math
import random
from typing import Iterator

from attrs import frozen

from .game_rule import GameRule
import core.protocols as proto
import core.figures.figure as fig

PRIVATES_FLAT_COUNT = 10
PRIVATES_RATIO = .1
PRIVATES_DECREASE_FROM_CAPITALS_RATIO = 5
PRIVATES_SPAWN_SPEED_MULTIPLIER = .1
PRIVATES_WEIGHTS = {
    fig.Settlement: 1,
    fig.PrivateLightFactory: .3,
    fig.PrivateHeavyFactory: .05,
}


@frozen
class PrivateFiguresSpawner(GameRule):
    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        player = session.master.current_player
        cells = session.cells
        player_cells = cells.with_owner(player)

        empties = player_cells - cells.not_empty()
        privates = player_cells.with_flag(proto.Private)

        target_count = (PRIVATES_FLAT_COUNT +
                        (len(empties) + len(privates)) * PRIVATES_RATIO -
                        len(player_cells & cells.with_figure(fig.Capital)) * PRIVATES_DECREASE_FROM_CAPITALS_RATIO)
        if target_count <= 0:
            return
        yield
        progress = len(privates) / target_count
        to_spawn = math.ceil(target_count * (1 - progress) * PRIVATES_SPAWN_SPEED_MULTIPLIER)
        to_spawn = max(0, min(to_spawn, len(empties)))

        private_figures, weights = zip(*PRIVATES_WEIGHTS.items())  # Jaxx22
        for cell in random.sample(empties.as_list(), to_spawn):
            yield
            figure: type[fig.Figure] = random.choices(private_figures, weights=weights)[0]
            session.figures.add(figure, session.board.coordinates_of(cell))
