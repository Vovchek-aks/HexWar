from typing import Iterator

from attrs import frozen

from .game_rule import GameRule
import core.protocols as proto



@frozen
class FiguresTransformer(GameRule):
    def on_turn_end(self, session: proto.GameSession) -> Iterator[None]:
        board = session.board
        player = session.master.current_player
        cells_cache = session.cells
        cells = cells_cache.with_owner(player)
        figures = session.figures

        transformers = cells & session.cells.with_flag(proto.Transforms)
        for transformer in transformers:
            coord = board.coordinates_of(transformer)
            target = transformer.figure.FLAGS.get(proto.Transforms).get_target(coord, session)
            if target is not type(transformer.figure):
                figures.remove(transformer.figure)
                figures.add(target, board.coordinates_of(transformer))

        yield
