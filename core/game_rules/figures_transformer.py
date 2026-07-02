from typing import Iterator

from attrs import frozen

from .game_rule import GameRule
import core.protocols as proto
from core.distant_neighbors_getter import DistantNeighborsGetter
import core.figures.figure as fig

FROM_FRONT_TO_BUNKER_MAX_DISTANCE = 3


@frozen
class FiguresTransformer(GameRule):
    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        cells_cache = session.cells
        cells = cells_cache.with_owner(player)
        figures = session.figures

        turners = cells & session.cells.with_flag(proto.TurnsOthersIntoItself)
        for turner in turners:
            coord = board.coordinates_of(turner)
            for cell in turner.figure.FLAGS.get(proto.TurnsOthersIntoItself).get_targets(coord, session):
                figures.remove(cell.figure)
                figures.add(type(turner.figure), board.coordinates_of(cell))

        front = cells & cells_cache.at_front  # todo
        for bunker in cells & cells_cache.with_figure(fig.Bunker):
            neighbors = (DistantNeighborsGetter(bunker, board)
                         .get_all_not_farther_than(FROM_FRONT_TO_BUNKER_MAX_DISTANCE, include_cell=True))
            if not neighbors & front:
                figures.remove(bunker.figure)
                figures.add(fig.Abandonment, board.coordinates_of(bunker))

        yield
