from typing import Iterator
from time import perf_counter as time

from attrs import define, field

import core.protocols as proto
from statuses import Status, MISSING, ABORT_NEEDED
from observer import Event, OnEventSubscriber


@define
class AnnexationMapUpdater(proto.AnnexationMapUpdater):
    @classmethod
    def make(cls,
             session: proto.GameSession,
             moves_maker: proto.MovesMaker,
             annexation_map: proto.AnnexationMap) -> proto.AnnexationMapUpdater:
        self = cls(session, annexation_map)
        moves_maker.cells_to_annex_could_have_changed.subscribe(
            lambda: self._on_annexations_might_have_changed(session.master.current_player)
        )
        session.master.turn_has_passed.subscribe(self._on_annexations_might_have_changed)
        session.master.turn_had_started.subscribe(self._on_annexations_might_have_changed)
        self._on_annexations_might_have_changed(session.master.current_player)
        return self

    _session: proto.GameSession
    _map: proto.AnnexationMap
    _last_move_time: float = 0

    _players_queue: list[proto.Player] = field(init=False, factory=list)
    _process: Iterator[None] | Status = field(init=False, default=MISSING)

    _update_for_player_was_requested: Event[proto.Player, None] = field(init=False, factory=Event)
    _update_for_player_was_started: Event[proto.Player, None] = field(init=False, factory=Event)
    _update_for_player_was_finished: Event[proto.Player, None] = field(init=False, factory=Event)

    @property
    def is_active(self) -> bool:
        return self._process is not MISSING

    @property
    def map(self) -> proto.AnnexationMap:
        return self._map

    @property
    def update_for_player_was_requested(self) -> OnEventSubscriber[proto.Player, None]:
        return self._update_for_player_was_requested.subscriber

    @property
    def update_for_player_was_started(self) -> OnEventSubscriber[proto.Player, None]:
        return self._update_for_player_was_started.subscriber

    @property
    def update_for_player_was_finished(self) -> OnEventSubscriber[proto.Player, None]:
        return self._update_for_player_was_finished.subscriber

    def is_about_to_be_updated(self, player: proto.Player) -> bool:
        return player in self._players_queue

    def update(self) -> None:
        if self.is_active:
            if next(self._process, ABORT_NEEDED) is not ABORT_NEEDED:
                return
            self._update_for_player_was_finished.invoke(self._players_queue.pop(0))
            self._process = MISSING

        if self._players_queue:
            self._start_next()

    def append(self, player: proto.Player) -> None:
        self._update_for_player_was_requested.invoke(player)

        if (not self._players_queue) or player not in self._players_queue:
            self._players_queue.append(player)
            return

        if player is self._players_queue[0]:
            self._players_queue.pop(0)
            self._players_queue.append(player)
            self._start_next()
            return

        self._players_queue.remove(player)
        self._players_queue.append(player)

    def push(self, player: proto.Player) -> None:
        self._update_for_player_was_requested.invoke(player)

        if not self._players_queue:
            self._players_queue.append(player)
            return

        if player in self._players_queue[1:]:
            self._players_queue.remove(player)

        if player is not self._players_queue[0]:
            self._players_queue.insert(0, player)

        self._process = MISSING

    def _on_annexations_might_have_changed(self, player: proto.Player) -> None:
        self._last_move_time = time()

        cells = self._session.cells
        neighbors = ((cells.with_owner(player) & cells.at_front)  # todo
                     .at_outer_boundry(self._session.board)
                     .players())
        for neighbor in neighbors:
            self.append(neighbor)
        self.push(player)

    def _start_next(self) -> None:
        assert self._players_queue

        skips = 60 if time() - self._last_move_time <= 1 else 10
        self._process = self._map.update_for(self._players_queue[0], initial_frame_skips=skips)
        self._update_for_player_was_started.invoke(self._players_queue[0])
