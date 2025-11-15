from attrs import frozen, field

import core.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class Master(proto.Master):
    _turn_has_passed: Event[proto.Player, None] = field(init=False, factory=Event)

    _players: list[proto.Player]

    @property
    def turn_has_passed(self) -> OnEventSubscriber[proto.Player, None]:
        return self._turn_has_passed.subscriber

    @property
    def current_player(self) -> proto.Player:
        return self._players[0]

    def pass_turn_to_next_player(self) -> None:
        self._players.append(self._players.pop(0))
        self._turn_has_passed.invoke(self.current_player)
