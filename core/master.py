from collections import defaultdict

from attrs import frozen, field

import core.protocols as proto
from observer import Event, OnEventSubscriber


@frozen
class Master(proto.Master):
    _players: list[proto.Player]
    _turn_of: dict[proto.Player, int] = field(factory=lambda: defaultdict(lambda: 1))

    _turn_had_started: Event[proto.Player, None] = field(init=False, factory=Event)
    _turn_has_passed: Event[proto.Player, None] = field(init=False, factory=Event)

    @property
    def current_turn(self) -> int:
        return self._turn_of[self.current_player]

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

    def turn_of(self, player: proto.Player) -> int:
        return self._turn_of[player]

    def get_next_player(self, session: proto.GameSession) -> proto.Player:
        self._remove_empty_players(session)

        if len(self._players) == 1:
            return self._players[0]

        return self._players[1]

    def pass_turn_to_next_player(self, session: proto.GameSession) -> None:
        previous_player = self.current_player
        self._players.append(self._players.pop(0))
        self._remove_empty_players(session)
        self._turn_of[previous_player] += 1

        self._turn_has_passed.invoke(previous_player)
        self._turn_had_started.invoke(self.current_player)

    def _remove_empty_players(self, session: proto.GameSession) -> None:
        to_remove = list[proto.Player]()
        for player in self._players:
            if not session.cells.with_owner(player):
                to_remove.append(player)

        for player in to_remove:
            self._players.remove(player)
