from attrs import frozen, field

import core.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class Master(proto.Master):
    _players: list[proto.Player]

    _turn_had_started: Event[proto.Player, None] = field(init=False, factory=Event)
    _turn_has_passed: Event[proto.Player, None] = field(init=False, factory=Event)

    @property
    def players(self) -> list[proto.Player]:
        return list(self._players)

    @property
    def current_player(self) -> proto.Player:
        return self._players[0]

    @property
    def turn_had_started(self) -> OnEventSubscriber[proto.Player, None]:
        return self._turn_had_started.subscriber

    @property
    def turn_has_passed(self) -> OnEventSubscriber[proto.Player, None]:
        return self._turn_has_passed.subscriber

    def pass_turn_to_next_player(self, session: proto.GameSession) -> None:
        previous_player = self.current_player
        self._players.append(self._players.pop(0))
        while not session.cells.with_owner(self.current_player):
            self._players.pop(0)

        self._turn_has_passed.invoke(previous_player)
        self._turn_had_started.invoke(self.current_player)
