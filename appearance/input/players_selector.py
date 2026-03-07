from attrs import define, field

import core.protocols as proto
from appearance.input.moves_inputer.input_actions import CellClickAction
from appearance.protocols import InputAction, MouseButtons, InputActionsReader
from core.master import Master
from core.player.inputers.bot_player_inputer import BotPlayerInputer
from core.player.inputers.wants_to_be_event_player_inputer import WantsToBeEventPlayerInputer
from observer import Event, OnEventSubscriber
from statuses import MISSING


@define
class PlayersSelector:
    @classmethod
    def make(cls, session: proto.GameSession, actions_reader: InputActionsReader) -> "PlayersSelector":
        assert all(isinstance(player.inputer, BotPlayerInputer) for player in session.master.players)

        self = cls(session)
        actions_reader.action_was_read.subscribe(self._on_action_was_read)
        return self

    _session: proto.GameSession
    _selected_players: list[proto.Player] = field(factory=list)

    _selected_players_were_changed: Event[list[proto.Player], None] = field(init=False, factory=Event)

    @property
    def has_selected(self) -> bool:
        return bool(self._selected_players)

    @property
    def selected_players_were_changed(self) -> OnEventSubscriber[list[proto.Player], None]:
        return self._selected_players_were_changed.subscriber

    def make_master(self) -> proto.Master:
        master = self._session.master
        bots = [player
                for player in master.players
                if player not in self._selected_players]

        players = list[proto.Player]()
        for player in master.players:
            if player in self._selected_players:
                player.change_inputer(WantsToBeEventPlayerInputer())
                players.append(player)

        return Master(players + bots)

    def _on_action_was_read(self, action: InputAction, _: bool) -> None:
        match action:
            case CellClickAction(coord=click_coord, buttons=MouseButtons(is_left=True)):
                ...
            case _:
                return

        owner = self._session.board[click_coord].owner
        if owner is MISSING:
            return

        self._toggle(owner)

    def _toggle(self, player: proto.Player) -> None:
        if player in self._selected_players:
            self._selected_players.remove(player)
        else:
            self._selected_players.append(player)

        self._selected_players_were_changed.invoke(self._selected_players)
