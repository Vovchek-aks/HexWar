from attrs import frozen

import core.protocols as proto


@frozen
class GameRuleStates(proto.GameRuleStates):
    _states: dict[type[proto.GameRuleState], proto.GameRuleState]

    @property
    def all(self) -> dict[type[proto.GameRuleState], proto.GameRuleState]:
        return dict(self._states)

    def get[T: proto.GameRuleState](self, game_rule_state_type: type[T]) -> T:
        return self._states[game_rule_state_type]
