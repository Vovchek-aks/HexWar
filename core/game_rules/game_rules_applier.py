from typing import Iterator, Callable

from attrs import frozen

from core import protocols as proto
from mathematics.vector import Vector2Int
from my_types import ContextManager
from . import Annexer, FiguresTransformer, PrivateFiguresSpawner, FiguresUpdateFlagCaller


@frozen
class GameRulesApplier(proto.GameRulesApplier):
    @classmethod
    def with_default_rules(cls,
                           session: proto.GameSession,
                           annexation_map: proto.AnnexationMapUpdater,
                           multiple_cells_change: Callable[[proto.Cells], ContextManager[None]],
                           on_changed_cell_owner: Callable[[Vector2Int], None]) -> proto.GameRulesApplier:
        return cls(session,
                   [
                       FiguresUpdateFlagCaller(),
                       Annexer(multiple_cells_change,
                               on_changed_cell_owner,
                               annexation_map),
                       FiguresTransformer(),
                       PrivateFiguresSpawner(),
                   ])

    _session: proto.GameSession
    _game_rules: list[proto.GameRule]

    def on_turn_start(self) -> Iterator[None]:
        for game_rule in self._game_rules:
            yield from game_rule.on_turn_start(self._session)

    def on_turn_end(self) -> Iterator[None]:
        for game_rule in self._game_rules:
            yield from game_rule.on_turn_end(self._session)
