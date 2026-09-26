from attrs import frozen

import core.protocols as proto
from .abandonments_spreader import AbandonmentsSpreaderState


@frozen
class GameRuleStates(proto.GameRuleStates):
    @classmethod
    def for_default_rules(cls, board: proto.Board, master: proto.Master) -> proto.GameRuleStates:
        return cls({
            AbandonmentsSpreaderState: AbandonmentsSpreaderState(board, master),
        })

    _states: dict[type[proto.GameRuleState], proto.GameRuleState]

    @property
    def all(self) -> dict[type[proto.GameRuleState], proto.GameRuleState]:
        return dict(self._states)

    def get[T: proto.GameRuleState](self, game_rule_state_type: type[T]) -> T:
        return self._states[game_rule_state_type]
